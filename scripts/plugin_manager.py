"""Install or uninstall the local plugin without replacing unrelated Codex configuration."""
from pathlib import Path
import argparse
import json
import os
import re
import shutil
import tomllib
from urllib.parse import quote

NAME = 'codex-game-studios'
MARKER = '.studio-plugin-owned.json'


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.studio-tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    os.replace(temp, path)


def plugin_source():
    base = Path(__file__).resolve().parents[1]
    return base if (base / 'plugin.json').exists() else base / 'plugins' / NAME


def locations(home):
    home = Path(home).resolve()
    return home, home / '.codex/plugins/local-source' / NAME, home / '.agents/plugins/marketplace.json'


def install(home, source=None):
    home, dest, market = locations(home)
    source = Path(source or plugin_source()).resolve()
    manifest = json.loads((source / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('name') != NAME:
        raise ValueError('unexpected plugin source identity')
    if source == dest or source.is_relative_to(dest):
        raise ValueError('install from the distribution folder, not the installed copy')
    catalog = json.loads(market.read_text(encoding='utf-8')) if market.exists() else {
        'name': 'local-game-studios', 'interface': {'displayName': 'Local Game Studios'}, 'plugins': []}
    if not isinstance(catalog.get('plugins'), list) or not isinstance(catalog.get('name'), str):
        raise ValueError('existing marketplace has an unsupported shape; left untouched')
    existing = [p for p in catalog['plugins'] if p.get('name') == NAME]
    if dest.exists():
        if not (dest / MARKER).is_file():
            raise ValueError('installation destination is not owned by this installer')
        state = json.loads((dest / MARKER).read_text(encoding='utf-8'))
        if state.get('home') != str(home):
            raise ValueError('installation ownership mismatch')
        # Idempotent reinstall; intentional upgrades use uninstall then install.
        return {'status': 'already-installed', 'path': str(dest), 'marketplace': str(market),
                'open': f'codex://plugins/{NAME}?marketplacePath={quote(str(market), safe="") }'}
    if existing:
        raise ValueError('a plugin with this name already exists in the marketplace; left untouched')
    entry = {'name': NAME, 'source': {'source': 'local', 'path': './' + dest.relative_to(home).as_posix()},
             'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}
    # Validate config before writing anything. Keep user model, auth and other plugin tables unchanged.
    config = home / '.codex/config.toml'
    old = config.read_text(encoding='utf-8') if config.exists() else ''
    parsed = tomllib.loads(old)
    key = NAME + '@' + catalog['name']
    if key in parsed.get('plugins', {}):
        raise ValueError('this plugin already has a config table; left untouched')
    block = '\n# BEGIN codex-game-studios installer\n[plugins.' + json.dumps(key) + ']\nenabled = true\n# END codex-game-studios installer\n'
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest)
    state = {'plugin': NAME, 'home': str(home), 'entry': entry, 'config_block': block,
             'config_key': key,
             'marketplace_created': not market.exists(), 'config_created': not config.exists(), 'original_config_empty': not old}
    try:
        dump(dest / MARKER, state)
        catalog['plugins'].append(entry)
        dump(market, catalog)
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(old + block, encoding='utf-8')
    except OSError:
        # Leave an owned install and journal for a safe uninstall/retry; never delete unrelated data.
        raise
    return {'status': 'installed', 'path': str(dest), 'marketplace': str(market),
            'open': f'codex://plugins/{NAME}?marketplacePath={quote(str(market), safe="")}'}


def uninstall(home):
    home, dest, market = locations(home)
    if not dest.exists():
        return {'status': 'not-installed'}
    if dest.is_symlink() or not dest.resolve().is_relative_to((home / '.codex/plugins/local-source').resolve()):
        raise ValueError('refusing to remove a destination outside the managed plugin directory')
    state = json.loads((dest / MARKER).read_text(encoding='utf-8'))
    if state.get('plugin') != NAME or state.get('home') != str(home):
        raise ValueError('installation ownership mismatch')
    config = home / '.codex/config.toml'
    config_text = config.read_text(encoding='utf-8') if config.exists() else None
    cleaned = config_text
    if config_text is not None:
        if state['config_block'] in config_text:
            cleaned = config_text.replace(state['config_block'], '', 1)
        else:
            # Codex may reserialize TOML and remove comments. Accept equivalent native formatting,
            # but never remove a table whose values or additional fields were changed by the user.
            key = state.get('config_key')
            current = tomllib.loads(config_text).get('plugins', {}).get(key)
            if current is None:
                cleaned = config_text  # already removed by the native plugin browser
            elif current == {'enabled': True}:
                headers = [json.dumps(key), "'" + key + "'"]
                pattern = r'(?ms)^\[plugins\.(?:' + '|'.join(re.escape(h) for h in headers) + r')\][ \t]*\r?\n.*?(?=^\[|\Z)'
                cleaned, count = re.subn(pattern, '', config_text, count=1)
                if count != 1:
                    raise ValueError('cannot safely locate rewritten plugin table; use native plugin controls')
            else:
                raise ValueError('plugin config block was modified; restore it or remove this plugin through Codex before retrying')
    if market.exists():
        catalog = json.loads(market.read_text(encoding='utf-8'))
        catalog['plugins'] = [p for p in catalog.get('plugins', []) if p != state['entry']]
        dump(market, catalog)
    if config.exists():
        config.write_text(cleaned, encoding='utf-8')
    # Verified exact absolute target and ownership above; game workspaces are never traversed.
    shutil.rmtree(dest)
    return {'status': 'uninstalled', 'workspaces': 'preserved',
            'next': 'Restart Codex; use its plugin browser to remove any cached installed entry if shown.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['install', 'uninstall', 'status'])
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'install':
            result = install(args.home, args.source)
        elif args.command == 'uninstall':
            result = uninstall(args.home)
        else:
            _, dest, market = locations(args.home)
            result = {'installed': (dest / MARKER).is_file(), 'path': str(dest), 'marketplace': str(market)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, 'plugin-manager: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
