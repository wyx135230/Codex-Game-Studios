"""Check project configuration against the installed CLI without changing user settings."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
exe = shutil.which('codex.cmd') or shutil.which('codex')
if not exe:
    raise SystemExit('Codex CLI not installed; use Codex desktop or install the CLI')
with tempfile.TemporaryDirectory(prefix='studio-codex-probe-') as tmp:
    base = Path(tmp)
    # Isolate from user-global config so the probe does not rewrite or depend on it.
    home = base / 'home'
    home.mkdir()
    project = base / 'project'
    (project / '.git').mkdir(parents=True)
    shutil.copytree(ROOT / '.codex', project / '.codex')
    (home / 'config.toml').write_text('[projects.' + repr(str(project)).replace("'", '"').replace('\\', '\\\\') + ']\ntrust_level = "trusted"\n')
    env = dict(os.environ, CODEX_HOME=str(home))
    result = subprocess.run([exe, 'features', 'list'], cwd=project, env=env,
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
    print(result.stdout, end='')
    print(result.stderr, end='')
    raise SystemExit(result.returncode)
