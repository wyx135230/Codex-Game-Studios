"""Generate native Codex entrypoints from the migrated role and event contracts."""
from pathlib import Path
import json
import re
from migrate_source import ROOT, write

RUNTIME = '''# Codex runtime contract

This file takes precedence over inherited platform-specific examples in the migrated references.
User instructions and host sandbox policy always take precedence over studio conventions.

## Skills and tools

Invoke repository skills as `$start`, `$dev-story`, etc., or ask in natural language.
Historical `/name` examples mean the skill of that name, not a new built-in Codex slash command.
Read the named SKILL.md and its referenced files; never assume a Claude Skill tool exists.
`$ARGUMENTS` means the user's invocation arguments. `STUDIO_SKILL_DIR` is a convention,
not an injected variable: resolve it to `.agents/skills/<name>` if encountered.
Run every configuration command shown at the start of a skill BEFORE its phases, from
the repository root. Codex does not execute `!` backtick injection syntax.
`Read`, `Glob`, `Grep`, `Write`, `Edit`, `Bash` and `AskUserQuestion` in references describe
operations: use available file/search/shell/apply_patch/question tools. Use `rg` for search.
For a required user decision, ask in chat and wait if no question tool is available.
Do not repeat an approval already granted for the current scope; prepare the concrete draft first.

## Roles and delegation

Native role definitions are `.codex/agents/<name>.toml`. Their `.md` siblings preserve
the original role contract for inspection, scripts, and older clients.
Use the available spawn tool with that role. If named custom agents are unavailable,
spawn a generic worker with the COMPLETE role body and relevant runtime/rules instructions.
If spawning itself is unavailable, perform role steps sequentially and mark that fallback.
Do not claim independent review when the same agent performs both steps.
Skill `context: fork` metadata means run that skill as a bounded child task and await its result;
without spawning, run it sequentially with a separate artifact/report.
Delegate only when the user or the selected workflow calls for it. Preserve director → lead →
specialist hierarchy, independent-task parallelism, boundaries, named outputs and escalation.
Subagents report questions to the parent; the parent puts required decisions to the user.
They inherit parent permissions. Original `tools`, `allowed-tools`, `disallowedTools`,
`maxTurns`, `memory` and model aliases are preserved in compatibility metadata, not asserted
as Codex enforcement. Keep tool scope and turn budget in the brief and track it there.
Persistent role memory is ordinary project data in `.codex/agent-memory/<role>/MEMORY.md`;
read it on demand and write only within the authorized task. No implicit memory injection.

## Models

All agents inherit the user's selected Codex model. There are no Anthropic model aliases
or automatic per-skill model switches. The original low/standard/deep tiers remain advisory.
Choose a supported model in the client or set native agent model fields deliberately if desired.
Never promise cost savings or a capability based on the original model tier.

## Rules and lifecycle

At session start read `production/session-state/active.md` if present and the shared
coordination/coding references linked by AGENTS.md. Read `.codex/rules/index.md`, then load
each rule whose globs match any file you will touch. Nested AGENTS.md applies by directory.
`paths:` in the migrated rule files is routing metadata, not a native Codex rule loader.
Hooks require a trusted project and explicit hook trust in clients that support hooks.
`.codex/hooks.json` delegates native events to `scripts/studio.py`; it normalizes shell and
multi-file apply_patch payloads, calls the original validators and forwards their decisions.
PermissionRequest triggers the old permission notification; Stop triggers idle/completion
notification. Instruction-load logging is explicit (not a native event): log shared guidance
on start via the lifecycle command, and invoke `hook InstructionsLoaded` for additional reads.
Use `python scripts/studio.py hook SessionStart` at startup if native hooks are unavailable,
`hook PreCompact` before a planned context reset, and `hook Stop` before finishing. Payload
can be supplied with `--payload file.json` for all events. For manual tool checks use the
documented payload shapes and invoke PreToolUse / PostToolUse around the operation.
Read guards require a Read payload; native shell reads cannot always be recognized.
Never treat hooks as a sandbox: shell writes, external editors and specialized tools can bypass
file-level validators. Apply the same rules and run helpers explicitly in these cases.
Read/write warnings remain advisory where upstream made them advisory; validator denial blocks.

## Configuration and results

Preserve project.yaml resolution, local overrides, legacy mirrors, rigor expansion, automation
modes, evidence hashes, checkpoint recovery and all domain checks. Helpers emit observations,
not pass/fail verdicts; inspect their rows. Engine validation needs the chosen engine executable.
Keep unknown/missing evidence as NOT ASSESSED. No commits, pushes or publication without user
instruction. Upstream updates are opt-in and refer to the original source; never install them
directly over this Codex port. Use the import manifest to review and reapply compatible changes.
'''


def main():
    write(ROOT / '.codex/docs/runtime.md', RUNTIME)
    for file in sorted((ROOT / '.codex/agents').glob('*.md')):
        text = file.read_text(encoding='utf-8')
        front, body = text.split('---', 2)[1:]
        name = re.search(r'^name:\s*(.+)$', front, re.M)[1].strip()
        desc = re.search(r'^description:\s*(.+)$', front, re.M)[1].strip().strip('"')
        instructions = ('First read .codex/docs/runtime.md and applicable project rules. '
                        'The runtime contract supersedes platform-specific examples below. '
                        'Use the parent session model and permission policy. '
                        'Return unresolved questions to the parent.\n\n' + body.lstrip())
        write(file.with_suffix('.toml'), f'name = {json.dumps(name)}\ndescription = {json.dumps(desc)}\n'
              f'developer_instructions = {json.dumps(instructions, ensure_ascii=False)}\n')
    write(ROOT / '.codex/config.toml', '''# Model and permissions inherit user/client settings.
[agents]
enabled = true
max_concurrent_threads_per_session = 3
''')
    events = ['SessionStart', 'PreToolUse', 'PostToolUse', 'PermissionRequest',
              'PreCompact', 'Stop', 'SubagentStart', 'SubagentStop']
    hooks = {}
    for event in events:
        posix = 'python3 "$(git rev-parse --show-toplevel)/scripts/studio.py" hook ' + event
        windows = 'powershell.exe -NoProfile -Command "& python ((Join-Path (git rev-parse --show-toplevel) \'scripts/studio.py\')) hook ' + event + '; exit $LASTEXITCODE"'
        hooks[event] = [{'matcher': '', 'hooks': [{'type': 'command', 'command': posix,
                                                   'commandWindows': windows, 'timeout': 120}]}]
    write(ROOT / '.codex/hooks.json', json.dumps({'hooks': hooks}, indent=2) + '\n')
    rules = ['# Rule routing\n\nRead matching files before editing. Globs are relative to repository root.\n']
    for file in sorted((ROOT / '.codex/rules').glob('*.md')):
        if file.name == 'index.md':
            continue
        text = file.read_text(encoding='utf-8')
        front = text.split('---', 2)[1] if text.startswith('---') else ''
        patterns = re.findall(r'^\s+-\s+"([^"]+)"', front, re.M)
        rules.append(f'- `{file.name}`: ' + (', '.join(f'`{p}`' for p in patterns) or 'all project tasks'))
    write(ROOT / '.codex/rules/index.md', '\n'.join(rules) + '\n')
    root = ROOT / 'AGENTS.md'
    text = root.read_text(encoding='utf-8')
    text = re.sub(r'(?m)^@(.+)$', r'Read `\1` when relevant (explicit file read; no @ import).', text)
    text = text.replace('49 coordinated Codex subagents', '49 coordinated Codex role definitions')
    text = text.replace('Codex starts here', 'the client loads and trusts this repository')
    text = text.replace('## Collaboration Protocol', '## Original Collaboration Protocol')
    text = ('# Runtime precedence\n\nRead `.codex/docs/runtime.md` first. It defines Codex tool mapping, '
            'native agents, explicit lifecycle fallback and rule routing. Existing user authorization '
            'covers necessary changes within its scope; do not ask again for each file. '
            'The original collaboration protocol below applies only to decisions not already authorized. '
            'Before touching files, read `.codex/rules/index.md` and all matching rules.\n\n' + text)
    write(root, text)
    # Replace instructions that would otherwise promise nonexistent platform mechanisms.
    write(ROOT / '.codex/docs/model-tiers.md', '''# Model tiers in Codex

All workflows and roles inherit the selected Codex session model. Original skill model aliases
are recorded in `.codex/compat/skill-metadata/` for migration auditing only. They do not switch
models or determine price. For simple read/format work use a suitable accessible model; for
implementation use the normal coding model; for cross-document gates use adequate reasoning.
Configure a supported custom agent `model` and `model_reasoning_effort` only deliberately.
''')
    coord = ROOT / '.codex/docs/coordination-rules.md'
    text = coord.read_text(encoding='utf-8').split('## Model Tier Assignment')[0]
    write(coord, text + '''## Codex orchestration

Read runtime.md for model inheritance, role loading and permission boundaries.
Use native subagents when the selected workflow requests delegation. Spawn independent tasks
before waiting; collect all results before dependent phases; report blocked and partial results.
For opt-in parallel teams read agent-teams.md. There is no separate experimental environment flag.
''')
    write(ROOT / '.codex/docs/agent-teams.md', '''# Parallel teams in Codex

Team workflows use native subagents in one parent session, bounded by the configured concurrency.
Opt in by requesting a team workflow. Partition file ownership and maintain the shared task list
in `production/`; collect artifacts before dependent phases. Do not use Claude team creation,
mailbox or task-list APIs. Communicate through available spawn/message/wait tools. If they are
unavailable, execute roles sequentially and disclose the fallback; independent reviews remain
NOT ASSESSED. All agents inherit the parent sandbox and approvals. Never spawn sidebar chats
as an implementation substitute.
''')
    # Keep the real upstream repository for update discovery; off by default for the fork.
    update = ROOT / '.codex/hooks/update-check.sh'
    text = update.read_text(encoding='utf-8').replace('Donchitos/Codex-Game-Studios', 'Donchitos/Claude-Code-Game-Studios')
    write(update, text)
    config = ROOT / 'project.yaml'
    text = config.read_text(encoding='utf-8')
    write(config, text + '\n# Upstream releases need migration review before applying to this port.\nupdates:\n  check: false\n')
    print('Generated native agents, hooks, runtime contract and rule routing')


if __name__ == '__main__':
    main()
