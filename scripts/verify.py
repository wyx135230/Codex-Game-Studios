"""Run offline port checks and representative retained helpers; write a machine-readable report."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from studio import ROOT, bash_path, shell


def main():
    checks = []
    def record(name, result, expected=0, contains=None):
        ok = result.returncode == expected and (contains is None or contains in result.stdout)
        checks.append({'name': name, 'passed': ok, 'exit': result.returncode,
                       'output': (result.stdout + result.stderr)[-5000:]})
        print(('PASS ' if ok else 'FAIL ') + name, flush=True)
    record('runtime and inventory tests', subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace'))
    exe = bash_path()
    scripts = sorted((ROOT / '.codex').rglob('*.sh'))
    for file in scripts:
        record('syntax ' + file.relative_to(ROOT).as_posix(), subprocess.run(
            [exe, '-n', str(file)], capture_output=True, text=True, timeout=20))
    cases = [
        ('project-state.sh', [], 'source_files\t0'),
        ('skill-lint.sh', ['all'], 'checked\t74 of 74'),
        ('agent-check.sh', [], 'AGENTS: 49'),
        ('compat-inventory.sh', [], None),
        ('registry.sh', ['validate'], None),
        ('config-set.sh', ['modes.rigor', 'standard', '--dry-run'], None),
        ('inputs-check.sh', ['AGENTS.md', '.agents/skills/start/SKILL.md'], 'FOUND'),
        ('project-coherence.sh', [], None),
    ]
    for name, args, contains in cases:
        record('helper ' + name, shell('.codex/scripts/' + name, args, timeout=120), contains=contains)
    record('configuration resolution', shell('.codex/hooks/yaml-helper.sh', ['resolve_config']), contains='Resolved Config')
    record('CLI configuration parse', subprocess.run([sys.executable, str(ROOT / 'scripts/probe_codex.py')],
           cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45))
    report = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
              'shell_scripts': len(scripts), 'passed': all(c['passed'] for c in checks),
              'limitations': ['No live model-driven skill runs or engine builds were performed.',
                              'Hook trust and project trust must be reviewed in the destination client.']}
    (ROOT / 'docs/verification.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
