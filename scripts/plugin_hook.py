"""Dispatch plugin lifecycle hooks only inside initialized studio projects."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys


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
            runtime = root / 'scripts/studio.py'
            if not runtime.is_file():
                print('Studio runtime missing; rerun plugin setup.', file=sys.stderr)
                return 2
            result = subprocess.run([sys.executable, str(runtime), 'hook', sys.argv[1]],
                                    input=json.dumps(data), text=True, cwd=root)
            return result.returncode
        # Do not attach a parent studio's hooks to a distinct nested repository.
        if (root / '.git').exists():
            break
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
