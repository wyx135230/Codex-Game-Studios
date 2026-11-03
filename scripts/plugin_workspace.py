"""Bind a game workspace to installed plugin resources without copying the framework."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

PACKAGE = Path(__file__).resolve().parents[1]
BEGIN = '<!-- codex-game-studios:begin -->'
END = '<!-- codex-game-studios:end -->'
BRIDGE = f'''{BEGIN}
## Codex Game Studios plugin
Before studio work, read `.studio/installation.json` for the current `plugin_root`.
Read `<plugin_root>/framework/PLUGIN_RUNTIME.md` and follow the installed plugin skills.
Keep skills, roles, templates and common scripts in the plugin; do not copy them here.
Project configuration is `project.yaml`; game artifacts stay in this workspace.
If the bound plugin is missing, enable/reinstall it and run `$studio-setup` to rebind.
{END}
'''.encode('utf-8')


def safe(root, rel):
    path = root / rel
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError(f'workspace symlink escapes root or owns an external file: {rel}')
    return path


def initialize(root, template=None):
    root = Path(root).resolve()
    template = Path(template or PACKAGE / 'framework').resolve()
    if not template.is_dir() or root == template or root.is_relative_to(template):
        raise ValueError('choose a workspace outside the plugin template')
    if (PACKAGE / 'plugin.json').exists() and (root == PACKAGE or root.is_relative_to(PACKAGE)):
        raise ValueError('game workspaces must be outside the installed plugin')
    root.mkdir(parents=True, exist_ok=True)
    ledger = safe(root, '.studio/installation.json')
    new_workspace = not ledger.exists()
    prior = json.loads(ledger.read_text(encoding='utf-8')) if ledger.exists() else {'files': {}}
    if ledger.exists() and (prior.get('plugin') != 'codex-game-studios' or not isinstance(prior.get('files'), dict)):
        raise ValueError('existing workspace ledger belongs to another installation; preserved')
    created, preserved = [], []
    config = safe(root, 'project.yaml')
    instruction_name = 'AGENTS.override.md' if (root / 'AGENTS.override.md').is_file() else 'AGENTS.md'
    guide = safe(root, instruction_name)
    original = guide.read_bytes() if guide.exists() else b''
    # Replace only our marked bridge, or a provably unmodified legacy template.
    old_hash = prior['files'].get(instruction_name)
    if old_hash and hashlib.sha256(original).hexdigest() == old_hash:
        original = b''
    begin, end = BEGIN.encode(), END.encode()
    if original.count(begin) != original.count(end) or original.count(begin) > 1:
        raise ValueError('modified/incomplete studio instruction marker; preserved')
    if begin in original and original.index(end) < original.index(begin):
        raise ValueError('modified/incomplete studio instruction marker; preserved')
    if begin in original:
        start, stop = original.index(begin), original.index(end) + len(end)
        remainder = original[stop:]
        if remainder.startswith(b'\r\n'):
            remainder = remainder[2:]
        elif remainder.startswith(b'\n'):
            remainder = remainder[1:]
        updated = original[:start] + BRIDGE + remainder
    else:
        updated = original + (b'\n\n' if original else b'') + BRIDGE
    if not config.exists():
        shutil.copyfile(template / 'project.yaml', config)
        prior['files']['project.yaml'] = hashlib.sha256(config.read_bytes()).hexdigest()
        created.append('project.yaml')
    else:
        preserved.append('project.yaml')
    if not guide.exists():
        created.append(instruction_name)
    if guide.exists() and original:
        preserved.append(instruction_name)
    if not guide.exists() or guide.read_bytes() != updated:
        guide.write_bytes(updated)
    # Existing instructions are not owned in their entirety.
    prior['files'].pop(instruction_name, None)
    package = template.parent
    manifest_path = package / 'plugin.json'
    version = json.loads(manifest_path.read_text(encoding='utf-8'))['version'] if manifest_path.exists() else '0.2.0'
    prior.update({'plugin': 'codex-game-studios', 'version': version, 'root': str(root),
                  'hooks': 'plugin-managed', 'layout': 'plugin-resources',
                  'plugin_root': str(package), 'framework_root': str(template),
                  'instruction_file': instruction_name})
    ledger.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(prior, indent=2) + '\n'
    if not ledger.exists() or ledger.read_text(encoding='utf-8') != encoded:
        ledger.write_text(encoded, encoding='utf-8')
    return {'root': str(root), 'initialized': new_workspace, 'created': created, 'preserved': preserved,
            'next': 'Read the installed framework/PLUGIN_RUNTIME.md and run the plugin skill; no framework copy is needed.'}


def cleanup(root, apply=False):
    """Remove only ledger-owned, unchanged legacy framework files; never game artifacts."""
    root = Path(root).resolve()
    ledger = safe(root, '.studio/installation.json')
    obj = json.loads(ledger.read_text(encoding='utf-8'))
    if obj.get('plugin') != 'codex-game-studios' or not isinstance(obj.get('files'), dict):
        raise ValueError('existing workspace ledger belongs to another installation; preserved')
    candidates, preserved = [], []
    for rel, digest in list(obj['files'].items()):
        owned_framework = (rel.startswith(('.agents/skills/', '.codex/', 'studio-tests/'))
                           or rel in ('STUDIO.md', 'scripts/studio.py', 'scripts/verify.py', 'scripts/probe_codex.py'))
        if not owned_framework or rel.startswith('.codex/agent-memory/'):
            continue
        path = safe(root, rel)
        if not path.is_file():
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            preserved.append(rel)
            continue
        candidates.append(rel)
        if apply:
            path.unlink()
            del obj['files'][rel]
            parent = path.parent
            while parent != root:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
    if apply:
        ledger.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
    return {'dry_run': not apply, 'files': candidates, 'preserved_modified': preserved}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'cleanup'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--apply', action='store_true', help='actually remove unchanged legacy framework files')
    args = parser.parse_args()
    try:
        result = initialize(args.root) if args.command == 'init' else cleanup(args.root, args.apply)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
