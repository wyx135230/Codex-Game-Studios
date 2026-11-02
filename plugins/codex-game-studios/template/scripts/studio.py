"""Codex studio lifecycle adapter and portable command line entry point (Python 3.11+)."""
from __future__ import annotations
import argparse
import fnmatch
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def bash_path():
    explicit = os.environ.get('STUDIO_BASH')
    if explicit:
        return explicit
    if os.name == 'nt':
        git = shutil.which('git')
        candidates = [Path(git).parent.parent / 'bin/bash.exe'] if git else []
        candidates += [Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/bash.exe']
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        # System32/bash.exe is a WSL launcher, not a native Git Bash runtime.
        raise RuntimeError('Git Bash not found. Install Git for Windows or set STUDIO_BASH.')
    found = shutil.which('bash')
    if not found:
        raise RuntimeError('bash not found')
    return found


def shell(script, args=(), payload=None, timeout=60):
    env = dict(os.environ, STUDIO_PROJECT_DIR=str(ROOT), PYTHONUTF8='1')
    exe = bash_path()
    env['PATH'] = str(Path(exe).parent) + os.pathsep + env.get('PATH', '')
    return subprocess.run([exe, str(ROOT / script), *args], cwd=ROOT,
                          input=json.dumps(payload) if payload is not None else None,
                          capture_output=True, text=True, encoding='utf-8', errors='replace',
                          env=env, timeout=timeout)


def contained(path):
    p = Path(path)
    p = (ROOT / p).resolve() if not p.is_absolute() else p.resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError(f'path outside project: {path}')
    return p


def patch_files(patch, post=False):
    """Convert Codex patch operations to prospective Write payloads, before mutation."""
    if not isinstance(patch, str) or not patch.startswith('*** Begin Patch\n'):
        raise ValueError('expected a Codex *** Begin Patch document')
    lines = patch.splitlines()
    changes = []
    i = 1
    while i < len(lines):
        line = lines[i]
        if line == '*** End Patch':
            return changes
        if not line.startswith(('*** Add File: ', '*** Update File: ', '*** Delete File: ')):
            raise ValueError(f'unsupported patch header: {line}')
        kind, name = line[4:].split(' File: ', 1)
        src = contained(name)
        dest = src
        i += 1
        if i < len(lines) and lines[i].startswith('*** Move to: '):
            dest = contained(lines[i][13:])
            i += 1
        body = []
        while i < len(lines) and not lines[i].startswith('*** '):
            body.append(lines[i]); i += 1
        if i < len(lines) and lines[i] == '*** End of File':
            i += 1
        if post:
            content = dest.read_text(encoding='utf-8') if dest.exists() else ''
        elif kind == 'Delete':
            content = ''
        elif kind == 'Add':
            if any(not row.startswith('+') for row in body):
                raise ValueError('invalid Add File patch')
            content = '\n'.join(row[1:] for row in body) + ('\n' if body else '')
        else:
            old = src.read_text(encoding='utf-8').splitlines()
            cursor = 0
            output = []
            hunks = []
            for row in body:
                if row.startswith('@@'):
                    hunks.append((row[2:].strip(), []))
                else:
                    if not hunks:
                        hunks.append(('', []))
                    hunks[-1][1].append(row)
            for anchor, hunk in hunks:
                search_from = cursor
                if anchor:
                    anchors = [j for j in range(cursor, len(old)) if old[j].strip() == anchor]
                    if not anchors:
                        raise ValueError(f'patch anchor not found: {anchor}')
                    search_from = anchors[0] + 1
                before = [r[1:] for r in hunk if r.startswith((' ', '-'))]
                after = [r[1:] for r in hunk if r.startswith((' ', '+'))]
                if any(not r.startswith((' ', '-', '+')) for r in hunk):
                    raise ValueError('invalid patch hunk')
                matches = [j for j in range(search_from, len(old) - len(before) + 1)
                           if old[j:j + len(before)] == before]
                if not matches:
                    raise ValueError(f'patch context not found: {name}')
                start = matches[0]
                output.extend(old[cursor:start]); output.extend(after)
                cursor = start + len(before)
            output.extend(old[cursor:])
            content = '\n'.join(output) + ('\n' if output else '')
        changes.append({'file_path': str(dest), 'content': content})
        if dest != src:
            changes.append({'file_path': str(src), 'content': ''})
    raise ValueError('missing *** End Patch')


def policy(tool, inputs):
    """Apply the original deny contract; this is a guardrail, not an OS sandbox."""
    settings = json.loads((ROOT / '.codex/compat/upstream-settings.json').read_text())
    if tool in ('Bash', 'PowerShell'):
        command = inputs.get('command', inputs.get('cmd', ''))
        for item in settings['permissions']['deny']:
            prefix = tool + '('
            if item.startswith(prefix) and fnmatch.fnmatchcase(command.lower(), item[len(prefix):-1].lower()):
                raise ValueError('studio policy denies destructive shell command')
    path = inputs.get('file_path', '')
    if path and tool in ('Read', 'Write', 'Edit'):
        parts = Path(path.replace('\\', '/')).parts
        if any(p.startswith('.env') for p in parts):
            raise ValueError('studio policy denies access to .env files')
        if tool != 'Read' and Path(path).suffix.lower() in ('.uasset', '.umap'):
            raise ValueError('binary Unreal assets must be edited in the engine')


def hook(event, data):
    messages = []
    original = data.get('tool_name', '')
    inputs = data.get('tool_input', {})
    if not isinstance(inputs, dict):
        inputs = {'command': inputs}
    tool = {'exec_command': 'Bash', 'shell_command': 'Bash'}.get(original, original)
    if tool == 'Bash' and 'cmd' in inputs:
        inputs = dict(inputs, command=inputs['cmd'])
    payloads = [dict(data, tool_name=tool, tool_input=inputs)]
    if original == 'apply_patch':
        changes = patch_files(inputs.get('command', inputs.get('input', inputs.get('patch', ''))),
                              post=event == 'PostToolUse')
        payloads = [dict(data, tool_name='Write', tool_input=c) for c in changes]
    if event == 'PreToolUse':
        for payload in payloads:
            policy(payload['tool_name'], payload['tool_input'])
    specs = json.loads((ROOT / '.codex/compat/upstream-settings.json').read_text())['hooks']
    if event == 'PermissionRequest':
        specs_for_event = specs['Notification']
        payloads = [dict(data, notification_type='permission_prompt')]
    elif event == 'InstructionsLoaded':
        specs_for_event = [{'matcher': '', 'hooks': [{'command': 'log-instructions.sh'}]}]
    else:
        specs_for_event = specs.get(event, [])
    if event == 'SessionStart':
        for name in ('AGENTS.md', '.codex/docs/runtime.md', '.codex/rules/index.md'):
            shell('.codex/hooks/log-instructions.sh', payload=dict(data, file_path=name,
                  load_reason='studio_session_start'))
    if event == 'Stop':
        proc = shell('.codex/hooks/notify.sh', payload=dict(data, message='Codex studio turn complete'))
        if proc.returncode:
            messages.append(proc.stderr.strip())
    import re
    for payload in payloads:
        for group in specs_for_event:
            matcher = group.get('matcher', '')
            if event in ('PreToolUse', 'PostToolUse') and matcher and not re.search(matcher, payload['tool_name']):
                continue
            for spec in group['hooks']:
                name = Path(spec['command'].split('/')[-1].rstrip('"')).name
                proc = shell('.codex/hooks/' + name, payload=payload,
                             timeout=max(30, spec.get('timeout', 15)))
                if proc.returncode == 2:
                    raise ValueError(proc.stderr.strip() or proc.stdout.strip() or f'{name} blocked the action')
                if proc.returncode:
                    raise RuntimeError(f'{name} exited {proc.returncode}: {proc.stderr}')
                output = proc.stdout.strip()
                if output:
                    try:
                        obj = json.loads(output)
                        if obj.get('decision') == 'block':
                            raise ValueError(obj.get('reason', 'blocked by studio hook'))
                        context = obj.get('hookSpecificOutput', {})
                        if context.get('permissionDecision') == 'deny':
                            raise ValueError(context.get('permissionDecisionReason', 'blocked by studio hook'))
                        messages.append(context.get('additionalContext', obj.get('systemMessage', '')))
                    except json.JSONDecodeError:
                        messages.append(output)
                if proc.stderr.strip():
                    messages.append(proc.stderr.strip())
    result = '\n'.join(m for m in messages if m)
    if result:
        # Context is supported on these native events; manual commands print plain text.
        if event in ('PreToolUse', 'PostToolUse', 'SessionStart', 'SubagentStart'):
            return {'hookSpecificOutput': {'hookEventName': event, 'additionalContext': result}}
        return {'systemMessage': result}
    return {}


def doctor():
    exe = bash_path()
    probe = subprocess.run([exe, '-c', 'for x in bash awk sed grep find git; do command -v "$x" || exit 1; done'],
                           capture_output=True, text=True, timeout=20)
    if probe.returncode:
        raise RuntimeError('incomplete Bash tools: ' + probe.stderr)
    skills = list((ROOT / '.agents/skills').glob('*/SKILL.md'))
    agents = list((ROOT / '.codex/agents').glob('*.toml'))
    tomllib.loads((ROOT / '.codex/config.toml').read_text())
    for file in agents:
        obj = tomllib.loads(file.read_text(encoding='utf-8'))
        assert all(obj.get(k) for k in ('name', 'description', 'developer_instructions')), file
    print(json.dumps({'python': sys.version.split()[0], 'bash': exe,
                      'skills': len(skills), 'agents': len(agents), 'status': 'ok'}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    sub.add_parser('list')
    runner = sub.add_parser('run')
    runner.add_argument('helper')
    runner.add_argument('args', nargs=argparse.REMAINDER)
    ev = sub.add_parser('hook')
    ev.add_argument('event')
    ev.add_argument('--payload', type=Path)
    sub.add_parser('status')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            doctor()
        elif args.command == 'list':
            for file in sorted((ROOT / '.agents/skills').glob('*/SKILL.md')):
                print('$' + file.parent.name)
        elif args.command == 'run':
            if Path(args.helper).name != args.helper:
                raise ValueError('use a helper basename from .codex/scripts')
            file = '.codex/scripts/' + args.helper
            if not (ROOT / file).is_file():
                raise ValueError('unknown helper: ' + args.helper)
            result = shell(file, args.args, timeout=3600)
            print(result.stdout, end=''); print(result.stderr, end='', file=sys.stderr)
            return result.returncode
        elif args.command == 'status':
            result = shell('.codex/statusline.sh', payload={'cwd': str(ROOT)})
            print(result.stdout, end='')
            return result.returncode
        else:
            data = json.loads(args.payload.read_text(encoding='utf-8') if args.payload else sys.stdin.read() or '{}')
            print(json.dumps(hook(args.event, data), ensure_ascii=False))
        return 0
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        if args.command == 'hook' and args.event == 'PreToolUse':
            # Native JSON survives cmd.exe / PowerShell process exit-code normalization.
            print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                  'permissionDecision': 'deny', 'permissionDecisionReason': str(exc)}}, ensure_ascii=False))
            return 0
        if args.command == 'hook' and args.event == 'PostToolUse':
            print(json.dumps({'decision': 'block', 'reason': str(exc),
                  'hookSpecificOutput': {'hookEventName': 'PostToolUse',
                                         'additionalContext': str(exc)}}, ensure_ascii=False))
            return 0
        print(f'studio: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
