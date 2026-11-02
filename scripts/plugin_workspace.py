"""Initialize a writable studio workspace from the installed plugin's bundled template."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

PACKAGE = Path(__file__).resolve().parents[1]


def initialize(root, template=None):
    root = Path(root).resolve()
    template = Path(template or PACKAGE / 'template').resolve()
    if not template.is_dir() or root == template or root.is_relative_to(template):
        raise ValueError('choose a workspace outside the plugin template')
    if (PACKAGE / 'plugin.json').exists() and (root == PACKAGE or root.is_relative_to(PACKAGE)):
        raise ValueError('game workspaces must be outside the installed plugin')
    root.mkdir(parents=True, exist_ok=True)
    ledger = root / '.studio/installation.json'
    if not ledger.resolve().is_relative_to(root):
        raise ValueError('workspace installation ledger escapes root')
    new_workspace = not ledger.exists()
    prior = json.loads(ledger.read_text(encoding='utf-8')) if ledger.exists() else {'files': {}}
    if ledger.exists() and (prior.get('plugin') != 'codex-game-studios' or not isinstance(prior.get('files'), dict)):
        raise ValueError('existing workspace ledger belongs to another installation; preserved')
    created, preserved = [], []
    for source in sorted(template.rglob('*')):
        if not source.is_file():
            continue
        rel = source.relative_to(template).as_posix()
        # Plugin hooks are registered once by the host, not again by each project.
        if rel == '.codex/hooks.json':
            continue
        target = root / rel
        if not target.resolve().is_relative_to(root):
            raise ValueError(f'workspace symlink escapes root: {rel}')
        if target.exists():
            preserved.append(rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        prior['files'][rel] = hashlib.sha256(target.read_bytes()).hexdigest()
        created.append(rel)
    # Do not overwrite existing project instructions. A separate file keeps the studio contract accessible.
    guide = root / 'STUDIO.md'
    if not guide.resolve().is_relative_to(root):
        raise ValueError('workspace studio guide escapes root')
    if not guide.exists():
        shutil.copyfile(template / 'AGENTS.md', guide)
        prior['files']['STUDIO.md'] = hashlib.sha256(guide.read_bytes()).hexdigest()
    manifest_path = PACKAGE / 'plugin.json'
    version = json.loads(manifest_path.read_text(encoding='utf-8'))['version'] if manifest_path.exists() else '0.1.1'
    prior.update({'plugin': 'codex-game-studios', 'version': version, 'root': str(root),
                  'hooks': 'plugin-managed'})
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps(prior, indent=2) + '\n', encoding='utf-8')
    return {'root': str(root), 'initialized': new_workspace, 'created': created, 'preserved': preserved,
            'next': 'Read STUDIO.md and .codex/docs/runtime.md, then run the requested workspace skill.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init'])
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = initialize(args.root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
