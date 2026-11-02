"""Apply platform-semantic adaptations after importing the upstream content."""
import json
import re
from migrate_source import ROOT, write


def main():
    hooks_file = ROOT / '.codex/hooks.json'
    hooks_data = json.loads(hooks_file.read_text(encoding='utf-8'))
    for event, groups in hooks_data['hooks'].items():
        groups[0]['hooks'][0]['commandWindows'] = 'python -c "import os,runpy,subprocess,sys; p=subprocess.check_output([\'git\',\'rev-parse\',\'--show-toplevel\'],text=True).strip(); sys.argv=[\'studio.py\',\'hook\',\'' + event + '\']; runpy.run_path(os.path.join(p,\'scripts\',\'studio.py\'),run_name=\'__main__\')"'
    write(hooks_file, json.dumps(hooks_data, indent=2) + '\n')
    runtime = ROOT / '.codex/docs/runtime.md'
    text = runtime.read_text(encoding='utf-8')
    preload = '''At the start of a role task, read `.codex/compat/agent-metadata/<role>.yaml`.
Apply its tool scope and `maxTurns` as task-budget instructions (not sandbox guarantees).
For every skill in its `skills:` list, read `.agents/skills/<name>/SKILL.md` and the
relevant references as preloaded procedural guidance; do not start unrelated workflows.
If `memory: project` is present, read `.codex/agent-memory/<role>/MEMORY.md` when it exists
and maintain it within the authorized task. Ignore the recorded Anthropic model alias.

'''
    if 'At the start of a role task' not in text:
        write(runtime, text.replace('## Models\n', preload + '## Models\n'))
    # Resolve all remaining skill-relative helpers after the skills directory move.
    for base in ('.agents', '.codex', 'studio-tests', 'docs'):
        for file in (ROOT / base).rglob('*'):
            if not file.is_file() or file.suffix not in ('.md', '.sh', '.yaml'):
                continue
            text = file.read_text(encoding='utf-8')
            text = re.sub(r'\$\{STUDIO_SKILL_DIR\}/../../(hooks|scripts)/', r'.codex/\1/', text)
            text = text.replace('CLAUDE_SESSION_ID', 'STUDIO_SESSION_ID')
            text = text.replace('CLAUDE_PLUGIN_ROOT', 'PLUGIN_ROOT').replace('CLAUDE_PLUGIN_DATA', 'PLUGIN_DATA')
            text = text.replace('CLAUDE.local.md', 'AGENTS.override.md')
            text = text.replace('Donchitos/Codex-Game-Studios', 'Donchitos/Claude-Code-Game-Studios')
            text = text.replace('4-claude-md-stack.md', '4-agents-md-stack.md')
            text = text.replace('— frontmatter `model:` reads exactly `sonnet`', '— native agent TOML omits `model`')
            text = text.replace('— frontmatter `model:` reads exactly `opus`', '— native agent TOML omits `model`')
            text = text.replace('— frontmatter `model:` reads exactly `haiku`', '— native agent TOML omits `model`')
            if file.parent == ROOT / '.codex/agents':
                meta = ROOT / '.codex/compat/agent-metadata' / (file.stem + '.yaml')
                if not meta.exists():
                    write(meta, text.split('---', 2)[1].strip() + '\n')
                text = re.sub(r'(?m)^model:.*$', 'model: inherit', text)
            # @ imports are not supported by Codex. Explicit reads preserve engine pin routing.
            text = re.sub(r'(?m)^@((?:docs|\.codex)/[^\n`]+)$', r'Read `\1` explicitly.', text)
            text = text.replace('Model tier is `sonnet`', 'Model inherits the Codex session')
            text = text.replace('Model tier is `opus`', 'Model inherits the Codex session')
            text = text.replace('Model tier is `haiku`', 'Model inherits the Codex session')
            if file.name == 'agent-check.sh':
                text = text.replace('os.path.join(root, ".codex", "skills")', 'os.path.join(root, ".agents", "skills")')
            if file.name == 'compat-inventory.sh':
                text = text.replace('os.path.join(claude, "skills")', 'os.path.join(root, ".agents", "skills")')
                text = text.replace('os.path.join(claude, "settings.json")', 'os.path.join(claude, "compat", "upstream-settings.json")')
            if file.name == 'skill-lint.sh':
                text = text.replace('req = "name description argument-hint user-invocable allowed-tools"', 'req = "name description"')
            if file.as_posix().endswith('skill-test/SKILL.md'):
                for key in ('argument-hint', 'user-invocable', 'allowed-tools'):
                    text = text.replace(f'- `{key}:`\n', '')
                text = text.replace('The frontmatter checks (1, 6 and 7) read `SKILL.md`.',
                                    'Check 1 reads native SKILL.md; checks 6 and 7 also read `.codex/compat/skill-metadata/<name>.yaml` for the original fork and argument contract.')
            write(file, text)
    old_stack = ROOT / '.agents/skills/setup-engine/references/4-claude-md-stack.md'
    if old_stack.exists():
        # Keep the manifest's original target accounted for, with a redirect for historical callers.
        if not old_stack.with_name('4-agents-md-stack.md').exists():
            write(old_stack.with_name('4-agents-md-stack.md'), old_stack.read_text(encoding='utf-8'))
        write(old_stack, 'Read `4-agents-md-stack.md` in this directory. The technology stack is maintained in AGENTS.md.\n')
    for name, content in {
        'setup-requirements.md': '# Setup requirements\n\nUse the root README for installation. Python 3.11+, Bash 3.2+ with awk/sed/grep/find, Git, and a local Codex client are required. Windows needs Git Bash; set STUDIO_BASH if automatic discovery fails. Engine builds require the chosen editor and its test framework. Plugin installation uses plugin.json, .codex-plugin/plugin.json and hooks/hooks.json, with hook trust reviewed in Codex. No .codex/settings.json is used.\n',
        'settings-local-template.md': '# Personal settings in Codex\n\nUse project.local.yaml for studio preferences via $settings --local. Use the Codex client or ~/.codex/config.toml for model and sandbox preferences. Do not create settings.local.json or Claude permission allowlists. Hooks are registered in hooks.json and reviewed through the client. Studio preferences do not grant OS permissions.\n',
    }.items():
        write(ROOT / '.codex/docs' / name, content)
    dev = ROOT / '.agents/skills/dev-story/SKILL.md'
    write(dev, dev.read_text(encoding='utf-8').replace('adds `Bash(<that executable> *)` to `.codex/settings.local.json`.', 'uses the Codex client permission prompt for that executable; do not write Claude permission allowlists.'))
    skills_ref = ROOT / '.codex/docs/skills-reference.md'
    write(skills_ref, skills_ref.read_text(encoding='utf-8').replace('`skillOverrides` in your own `.codex/settings.local.json`', 'the Codex skill controls or the skill\'s `agents/openai.yaml` invocation policy'))
    for name in ('quick-start.md', 'context-management.md'):
        f = ROOT / '.codex/docs' / name
        text = f.read_text(encoding='utf-8').replace('settings.json', 'hooks.json')
        write(f, text)
    write(ROOT / '.worktreeinclude', '# Historical worktree copy list; Codex does not load this file automatically.\n# Copy authorized local studio preferences explicitly when preparing a worktree.\nproject.local.yaml\nAGENTS.override.md\n')
    config = ROOT / '.codex/docs/config-resolution.md'
    text = config.read_text(encoding='utf-8')
    # Keep the actual defaults and precedence documentation, replace obsolete injection mechanics.
    text = '''# Config resolution in Codex

Before a skill's phases, explicitly run its `bash .codex/hooks/yaml-helper.sh resolve_config`
command from the repository root (or use `python scripts/studio.py run` for other helpers).
Use the emitted values and provenance as-is; do not rederive them. For a system override pass
its name, for example `resolve_config combat`. Codex has no preprocessing shell injection,
per-skill allowed-tools grant, or automatically expanded skill environment variable.
The selected client sandbox and approval policy control execution. The remaining resolution
rules, defaults and provenance below are unchanged domain behavior.

''' + '## The block' + text.split('## The block', 1)[1]
    write(config, text)
    rules = ROOT / '.codex/docs/rules-reference.md'
    text = rules.read_text(encoding='utf-8')
    # Retain the detailed domain rule descriptions beneath the platform introduction.
    headings = list(re.finditer(r'(?m)^## ', text))
    tail = text[headings[0].start():] if headings else ''
    write(rules, '''# Path-specific rules in Codex

Read `.codex/rules/index.md` and load every rule matching a path before reading or changing it.
The `paths:` metadata is interpreted by the studio workflow, not a Codex automatic rule loader.
Files with no paths apply to every task. Nested AGENTS.md files add directory instructions.
Treat rules as guidance; run the validators explicitly if native hooks are unavailable.
Log extra instruction reads with `python scripts/studio.py hook InstructionsLoaded --payload file.json`.

''' + tail)
    hooks = ROOT / '.codex/docs/hooks-reference.md'
    text = hooks.read_text(encoding='utf-8')
    text = text.replace('Hooks are configured in `.codex/settings.json` and fire automatically:',
        'Native registration is `.codex/hooks.json`; review and trust it in Codex. The Python adapter maps native events and tool inputs to the following retained validators. Without hook support use the manual lifecycle commands in `runtime.md`.')
    text = text.replace('under `claude -p` it is cancelled if still running when the session ends',
                        'the Codex adapter waits for completion before returning')
    text = text.replace('Stop, async', 'Stop, synchronous adapter')
    text = text.replace('`.codex/settings.local.json`', '`scripts/studio.py hook InstructionsLoaded`')
    write(hooks, text)
    directory = ROOT / '.codex/docs/directory-structure.md'
    text = directory.read_text(encoding='utf-8').replace('# Agent definitions, skills, hooks, rules, docs', '# Native agents, hooks, rules, docs')
    text = text.replace('├── .codex/', '├── .agents/skills/             # 74 repository skills\n├── scripts/                    # Codex adapter and verification\n├── .codex/', 1)
    write(directory, text)
    # Regenerate native role bodies after semantic adaptation.
    for file in (ROOT / '.codex/agents').glob('*.md'):
        native = file.with_suffix('.toml')
        import tomllib
        obj = tomllib.loads(native.read_text(encoding='utf-8'))
        body = file.read_text(encoding='utf-8').split('---', 2)[2].lstrip()
        prefix = obj['developer_instructions'].split('\n\n', 1)[0]
        obj['developer_instructions'] = prefix + '\n\n' + body
        write(native, '\n'.join(f'{k} = {json.dumps(v, ensure_ascii=False)}' for k, v in obj.items()) + '\n')
        write(ROOT / '.codex/roles' / (file.stem + '.toml'),
              'developer_instructions = ' + json.dumps(obj['developer_instructions'], ensure_ascii=False) + '\n')
    # Codex CLI 0.125 uses registered roles; newer clients discover standalone agents.
    legacy = '# Compatible with Codex CLI 0.125 role registration.\n[features]\nmulti_agent = true\n\n[agents]\nmax_threads = 4\n'
    for file in sorted((ROOT / '.codex/agents').glob('*.toml')):
        obj = tomllib.loads(file.read_text(encoding='utf-8'))
        legacy += f'\n[agents.{json.dumps(obj["name"])}]\ndescription = {json.dumps(obj["description"])}\nconfig_file = "roles/{file.stem}.toml"\n'
    write(ROOT / '.codex/config.toml', legacy)
    write(ROOT / '.codex/config.legacy.toml', legacy)
    write(ROOT / '.codex/config.modern.toml', '[agents]\nenabled = true\nmax_concurrent_threads_per_session = 3\n')
    for file in (ROOT / 'docs/upstream').glob('*.md'):
        text = file.read_text(encoding='utf-8')
        banner = '> Historical upstream documentation, mechanically path-adapted for reference. For the supported Codex installation and upgrade procedure use the root README and docs/MIGRATION.md.\n\n'
        if not text.startswith(banner):
            write(file, banner + text)
    print('Adapted helper discovery, rule loading, configuration bootstrap and role contracts')


if __name__ == '__main__':
    main()
