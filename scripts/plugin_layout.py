"""Build plugin-owned workflows/resources with workspace-relative game artifacts."""
from pathlib import Path
import json
import re
import shutil


def resource_path(logical):
    if logical.startswith('.agents/skills/'):
        return 'skills/' + logical[len('.agents/skills/'):]
    return 'framework/' + logical


def markdown(text):
    # Mutable project mirrors and role memory are data, not installed resources.
    text = text.replace('.codex/docs/technical-preferences.md', '.studio/technical-preferences.md')
    text = text.replace('.codex/agent-memory/', '.studio/agent-memory/')
    text = text.replace('${STUDIO_SKILL_DIR}/../../hooks/', '<plugin-root>/framework/.codex/hooks/')
    text = re.sub(r'(?<![\w/])(?:\.\./)*\.agents/skills/', '<plugin-root>/skills/', text)
    text = re.sub(r'(?<![\w/])(?:\.\./)*\.codex/', '<plugin-root>/framework/.codex/', text)
    text = text.replace('scripts/studio.py', '<plugin-root>/scripts/studio.py')
    return text


def shell_text(text, rel):
    """Relocate static shell resources, leaving all project artifact paths alone."""
    text = text.replace('.codex/docs/technical-preferences.md', '.studio/technical-preferences.md')
    text = text.replace('.codex/agent-memory/', '.studio/agent-memory/')
    text = text.replace('cd "$(dirname "$0")/../.."', 'cd "$STUDIO_PROJECT_DIR"')
    text = text.replace('cd "$HERE/../.."', 'cd "$STUDIO_PROJECT_DIR"')
    # Python heredocs do not interpolate shell variables; use explicit environment roots.
    text = text.replace('os.path.join(root, ".codex"', 'os.path.join(os.environ.get("STUDIO_FRAMEWORK_ROOT", root), ".codex"')
    text = text.replace('os.path.join(root, ".agents", "skills")', 'os.environ.get("STUDIO_SKILLS_ROOT", os.path.join(root, ".agents", "skills"))')
    text = text.replace('os.path.join(root, "studio-tests"', 'os.path.join(os.environ.get("STUDIO_FRAMEWORK_ROOT", root), "studio-tests"')
    lines, heredoc = [], None
    pattern = re.compile(r'(?:\$(?:ROOT|_YH_ROOT|CCGS_ROOT)/)?(?P<path>\.codex/(?:hooks|scripts|docs|rules|agents|compat)(?:/[\w./*-]*)?|\.agents/skills(?:/[\w./*-]*)?)')
    for line in text.splitlines(keepends=True):
        if heredoc:
            lines.append(line)
            if line.strip() == heredoc:
                heredoc = None
            continue
        found = re.search(r"<<-?\s*['\"]([\w]+)['\"]", line)
        if not line.lstrip().startswith('#'):
            def replace(match):
                path = match['path']
                base = '${STUDIO_SKILLS_ROOT}' if path.startswith('.agents/') else '${STUDIO_FRAMEWORK_ROOT}/.codex/' + path[len('.codex/'):]
                if path.startswith('.agents/'):
                    base += path[len('.agents/skills'):]
                # Track quoting before the match; quoted expansions must retain spaces.
                quote, escaped = None, False
                for ch in line[:match.start()]:
                    if escaped:
                        escaped = False
                    elif ch == '\\' and quote != "'":
                        escaped = True
                    elif ch in ('"', "'"):
                        if quote == ch:
                            quote = None
                        elif quote is None:
                            quote = ch
                if quote == '"':
                    return base
                if quote == "'":
                    return "'\"" + base + "\"'"
                return '"' + base + '"'
            line = pattern.sub(replace, line)
        lines.append(line)
        if found:
            heredoc = found[1]
    up = '..' if rel == '.codex/statusline.sh' else '../..'
    bootstrap = f'''# Plugin resources are read-only; all game data is relative to the workspace.
STUDIO_FRAMEWORK_ROOT="${{STUDIO_FRAMEWORK_ROOT:-$(cd "$(dirname "${{BASH_SOURCE[0]}}")/{up}" && pwd)}}"
STUDIO_PROJECT_DIR="${{STUDIO_PROJECT_DIR:-$PWD}}"
STUDIO_SKILLS_ROOT="${{STUDIO_SKILLS_ROOT:-$STUDIO_FRAMEWORK_ROOT/../skills}}"
export STUDIO_FRAMEWORK_ROOT STUDIO_PROJECT_DIR STUDIO_SKILLS_ROOT
'''
    result = ''.join(lines)
    first, sep, rest = result.partition('\n')
    return first + sep + bootstrap + rest


RUNTIME = '''# Installed plugin runtime

The installed plugin owns all 74 full workflows, references, 49 role contracts, rules,
templates and helper scripts. Do not copy or symlink these into a game workspace.
`<plugin-root>` is the absolute package directory found from the loaded skill's path.
The game workspace is the user's selected project; run commands from that root.

Before any workflow, run `python "<plugin-root>/scripts/plugin_workspace.py" init --root "<workspace>"`.
This only binds configuration and a short AGENTS instruction bridge. Read its output,
the effective project AGENTS.md / AGENTS.override.md, and this file. Read the project's
checkpoint at production/session-state/active.md if present. Read the bundled runtime
at `<plugin-root>/framework/.codex/docs/runtime.md`, then the rule index and matching rules.
This installed runtime takes precedence over template assumptions in the bundled contract.

Use the full workflow at `<plugin-root>/skills/<name>/SKILL.md` and its relative references.
Resolve every `<plugin-root>` placeholder to the actual installation path before use.
Old `.agents/skills/` references mean plugin `skills/`. Old `.codex/` framework references
mean plugin `framework/.codex/`; mutable technical-preferences and agent-memory live under
workspace `.studio/`. Old `studio-tests/` means plugin `framework/studio-tests/`.
`docs/engine-reference/`, design/, src/, production/, assets/, tests/ and generated
architecture/configuration are project artifacts, created only when a selected workflow needs them.
Do not seed example engine references as a project's selected engine version.

Run helpers using `python "<plugin-root>/scripts/studio.py" run <helper.sh> <arguments>`.
For config resolution use `python "<plugin-root>/scripts/studio.py" helper .codex/hooks/yaml-helper.sh resolve_config <arguments>`.
Other bundled shell scripts can be invoked with the same `helper` command and a relative
framework path. It supplies the project/resource roots and preserves spaces in paths.
Before implementing, honor the workflow's phase-zero configuration commands and every reference phase.

Role contracts are in plugin `framework/.codex/agents/`, and compatibility metadata in
`framework/.codex/compat/agent-metadata/`. Load each required complete role contract and metadata
into a generic child agent when the host has no named role. Preserve tools/budget guidance,
skill preloads, model inheritance, delegation boundaries, artifacts and escalation. No role
registration files are copied to the project. With no child tool, run sequentially and disclose
that independent review was not performed. Never claim automatic native role registration.

Lifecycle hooks come from the plugin and require client trust. They only attach to a project
with our installation ledger. Without native hooks run the installed studio.py hook commands
explicitly. Hooks are guardrails, not a sandbox. Standard user permissions still apply.
Changing installed skills requires editing the owning source and releasing a new plugin;
never modify installed cache resources from a game workflow. Project-specific overrides are
ordinary project instructions/configuration and do not require a second skill library.

When upgrading, run setup in the new plugin to refresh the binding. Existing project data stays.
For a 0.1.x workspace, `plugin_workspace.py cleanup --root <workspace>` previews removal of
unchanged ledger-owned framework files; add --apply to remove only those files. Edited files,
agent memory and game artifacts are retained. Never delete legacy directories wholesale.
'''


def populate(root, package, write):
    framework = package / 'framework'
    for folder in ('.codex', '.github', 'design', 'docs', 'production', 'src', 'studio-tests'):
        shutil.copytree(root / folder, framework / folder, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', 'session-logs', 'active.md', 'plugin-verification.json', 'distribution-verification.json'))
    for name in ('AGENTS.md', 'project.yaml', 'LICENSE', '.gitignore', '.gitattributes', '.worktreeinclude', 'README.md', 'README.en.md', 'CONTRIBUTING.md', 'SECURITY.md'):
        if (root / name).exists():
            shutil.copyfile(root / name, framework / name)
    # Retain original test source for provenance; never put it into game workspaces.
    (framework / 'tests').mkdir()
    shutil.copyfile(root / 'tests/test_runtime.py', framework / 'tests/test_runtime.py')
    for folder in (root / '.agents/skills').iterdir():
        if folder.is_dir():
            shutil.copytree(folder, package / 'skills' / folder.name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for file in framework.rglob('*.sh'):
        write(file, shell_text(file.read_text(encoding='utf-8'), file.relative_to(framework).as_posix()))
    for base in (framework, package / 'skills'):
        for file in base.rglob('*.md'):
            write(file, markdown(file.read_text(encoding='utf-8')))
    for file in (package / 'skills').glob('*/SKILL.md'):
        text = file.read_text(encoding='utf-8')
        front, body = text.split('---', 2)[1:]
        prelude = '''## Installed plugin binding

Resolve this installed plugin root from this skill path. Read `<plugin-root>/framework/PLUGIN_RUNTIME.md`
and run its minimal workspace binding before the workflow below. Execute from the game workspace,
read references from this installed skill directory, and keep all framework files in the plugin.
This skill contains the full workflow; do not create or invoke a workspace skill copy.

'''
        write(file, '---' + front + '---\n\n' + prelude + body.lstrip())
    write(framework / 'PLUGIN_RUNTIME.md', RUNTIME)
    write(package / 'skills/studio-setup/SKILL.md', '''---
name: studio-setup
description: Bind this game workspace to installed Codex Game Studios resources without duplicating skills or framework files.
---

Locate this plugin root from this skill path. Run
`python "<plugin-root>/scripts/plugin_workspace.py" init --root "<workspace>"`.
Read the effective AGENTS instruction file, then `<plugin-root>/framework/PLUGIN_RUNTIME.md`.
Run installed `scripts/studio.py doctor` from the workspace. On initial binding run its
`hook SessionStart` once. Follow the installed `<plugin-root>/skills/start/SKILL.md` for onboarding.
Existing configuration is preserved. Do not copy skills, roles, templates or scripts into the workspace.
''')
    (package / 'scripts').mkdir(parents=True, exist_ok=True)
    for name in ('plugin_workspace.py', 'plugin_hook.py', 'studio.py'):
        shutil.copyfile(root / 'scripts' / name, package / 'scripts' / name)
    manifest = json.loads((root / 'docs/migration-manifest.json').read_text(encoding='utf-8'))
    resource_map = {row['target']: resource_path(row['target']) for row in manifest}
    write(framework / 'resource-map.json', json.dumps(resource_map, indent=2) + '\n')
