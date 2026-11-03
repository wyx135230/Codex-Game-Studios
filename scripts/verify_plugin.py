"""Verify the built plugin with a real package, temporary user home and workspace."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from plugin_manager import install, uninstall
from plugin_workspace import initialize
from build_plugin import VERSION

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins/codex-game-studios'


def main():
    results = []
    def check(name, condition, detail=''):
        results.append({'name': name, 'passed': bool(condition), 'detail': detail})
        print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    archive = ROOT / 'dist' / f'codex-game-studios-{VERSION}.zip'
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        check('archive integrity', z.testzip() is None)
        check('75 plugin skill entrypoints', len([p for p in names if p.startswith('skills/') and p.endswith('/SKILL.md')]) == 75)
        manifest = json.loads(z.read('plugin.json'))
        overlay = json.loads(z.read('.codex-plugin/plugin.json'))
        check('manifest identity', manifest['name'] == overlay['name'] == 'codex-game-studios')
        check('listing subtitle', len(manifest['extensions']['com.openai']['interface']['shortDescription']) <= 30)
        missing = [entry['target'] for entry in json.loads(z.read('framework/docs/migration-manifest.json'))
                   if json.loads(z.read('framework/resource-map.json'))[entry['target']] not in names]
        check('all imported files bundled', not missing, str(missing))
        check('no project secrets or active session data', not any(
            Path(p).name.startswith('.env') or p.endswith('project.local.yaml') or p.endswith('session-state/active.md') for p in names))
    with tempfile.TemporaryDirectory(prefix='studio-plugin-verification-') as tmp:
        base = Path(tmp).resolve()
        home = base / 'home'
        game = base / 'game'
        unpacked = base / 'unpacked-plugin'
        with zipfile.ZipFile(archive) as z:
            z.extractall(unpacked)
        obj = install(home, unpacked)
        check('real package install', obj['status'] == 'installed')
        check('real package reinstall', install(home, unpacked)['status'] == 'already-installed')
        installed = Path(obj['path'])
        setup = initialize(game, installed / 'framework')
        check('workspace initialization', setup['initialized'] and (game / 'AGENTS.md').exists() and not (game / '.agents').exists())
        proc = subprocess.run([sys.executable, str(installed / 'scripts/studio.py'), 'doctor'], cwd=game,
                              capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
        check('installed workspace doctor', proc.returncode == 0, proc.stdout + proc.stderr)
        check('minimal initial project footprint', {p.relative_to(game).as_posix() for p in game.rglob('*') if p.is_file()} == {'AGENTS.md', 'project.yaml', '.studio/installation.json'})
        payload = {'cwd': str(game), 'session_id': 'plugin-verification', 'tool_name': 'exec_command',
                   'tool_input': {'cmd': 'git status --short'}}
        proc = subprocess.run([sys.executable, str(installed / 'scripts/plugin_hook.py'), 'PreToolUse'],
                              cwd=game, input=json.dumps(payload), capture_output=True, text=True, timeout=90)
        check('installed native hook adapter', proc.returncode == 0 and
              json.loads(proc.stdout).get('hookSpecificOutput', {}).get('permissionDecision') != 'deny', proc.stdout + proc.stderr)
        payload['tool_input']['cmd'] = 'git reset --hard HEAD'
        proc = subprocess.run([sys.executable, str(installed / 'scripts/plugin_hook.py'), 'PreToolUse'],
                              cwd=game, input=json.dumps(payload), capture_output=True, text=True, timeout=30)
        check('installed native hook denies destructive command', proc.returncode == 0 and
              json.loads(proc.stdout).get('hookSpecificOutput', {}).get('permissionDecision') == 'deny', proc.stdout + proc.stderr)
        powershell = shutil.which('powershell.exe')
        if powershell:
            command = json.loads((installed / 'hooks/hooks.json').read_text())['hooks']['PreToolUse'][0]['hooks'][0]['commandWindows']
            proc = subprocess.run([powershell, '-NoProfile', '-Command', command], cwd=game,
                                  env=dict(os.environ, PLUGIN_ROOT=str(installed)), input=json.dumps(payload),
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            check('declared Windows hook command forwards denial', proc.returncode == 0 and
                  json.loads(proc.stdout).get('hookSpecificOutput', {}).get('permissionDecision') == 'deny', proc.stdout + proc.stderr)
        # Test native marketplace registration with an isolated CODEX_HOME, never the real user profile.
        exe = shutil.which('codex.cmd') or shutil.which('codex')
        if exe:
            proc = subprocess.run([exe, 'plugin', 'marketplace', 'add', str(home)], cwd=base,
                                  env=dict(os.environ, CODEX_HOME=str(home / '.codex')),
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            check('native CLI marketplace registration', proc.returncode == 0, proc.stdout + proc.stderr)
            native_home = base / 'native-market-home'
            native_home.mkdir()
            proc = subprocess.run([exe, 'plugin', 'marketplace', 'add', str(ROOT / 'dist/codex-game-studios-marketplace')],
                                  cwd=base, env=dict(os.environ, CODEX_HOME=str(native_home)),
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            check('native distribution marketplace registration', proc.returncode == 0, proc.stdout + proc.stderr)
        (game / 'src').mkdir(exist_ok=True)
        (game / 'src/player.gd').write_text('user game content\n', encoding='utf-8')
        check('real package uninstall', uninstall(home)['status'] == 'uninstalled')
        check('game survives uninstall', (game / 'src/player.gd').read_text() == 'user game content\n')
        check('owned source removed', not installed.exists())
        powershell = shutil.which('powershell.exe')
        if powershell:
            ps_home = base / 'powershell-home'
            proc = subprocess.run([powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                                  str(ROOT / 'install.ps1'), '-HomeDirectory', str(ps_home), '-NoOpen'],
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45)
            check('PowerShell install launcher', proc.returncode == 0, proc.stdout + proc.stderr)
            proc = subprocess.run([powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                                  str(ROOT / 'uninstall.ps1'), '-HomeDirectory', str(ps_home)],
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            check('PowerShell uninstall launcher', proc.returncode == 0, proc.stdout + proc.stderr)
    report = {'version': VERSION, 'passed': all(r['passed'] for r in results), 'checks': results,
              'limitations': ['Desktop UI install/trust clicks were not automated.', 'No engine builds or model-driven full workflow runs.']}
    (ROOT / 'docs/plugin-verification.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
