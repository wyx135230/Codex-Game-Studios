"""Dispatch plugin lifecycle hooks only inside initialized studio projects."""
from pathlib import Path
import runpy
import json
import subprocess
import sys
import os


def main():
    data = json.loads(sys.stdin.read() or '{}')
    cwd = Path(data.get('cwd') or Path.cwd()).resolve()
    if cwd.is_file():
        cwd = cwd.parent
    for root in [cwd, *cwd.parents]:
        ledger = root / '.studio/installation.json'
        if ledger.is_file():
            obj = json.loads(ledger.read_text(encoding='utf-8'))
            if obj.get('plugin') != 'codex-game-studios':
                return 0
            package = Path(__file__).resolve().parents[1]
            if (package / 'framework').is_dir():
                # A host update may move its versioned cache. Refresh only this binding.
                # runpy-based Windows hooks have no script directory on sys.path.
                # Loading source this way also avoids writing __pycache__ into the plugin.
                initialize = runpy.run_path(str(package / 'scripts/plugin_workspace.py'))['initialize']
                initialize(root, package / 'framework')
            runtime = package / 'scripts/studio.py'
            if not runtime.is_file():
                print('Studio runtime missing; rerun plugin setup.', file=sys.stderr)
                return 2
            result = subprocess.run([sys.executable, str(runtime), 'hook', sys.argv[1]],
                                    input=json.dumps(data), text=True, cwd=root,
                                    env=dict(os.environ, STUDIO_PROJECT_DIR=str(root)))
            return result.returncode
        # Do not attach a parent studio's hooks to a distinct nested repository.
        if (root / '.git').exists():
            break
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
