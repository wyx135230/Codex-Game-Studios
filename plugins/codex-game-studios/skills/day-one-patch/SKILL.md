---
name: day-one-patch
description: "Day-one launch patch — focused fix for known issues found after gold master. Mini-sprint with QA gate and rollback."
---

# day-one-patch — plugin entrypoint

The complete workflow and references are bundled in `template/.agents/skills/day-one-patch/`.
Locate this plugin root from the loaded SKILL.md path (two parent directories above `skills/`).
Use that absolute path in commands; do not assume the shell expands a PLUGIN_ROOT variable.
First choose the current game workspace from the user's task. If no workspace is available,
ask for its path. Run `python "<plugin-root>/scripts/plugin_workspace.py" init --root "<workspace>"`.
This fills missing template files and preserves existing ones. Inspect any preserved conflicts.
If the result says `initialized: true`, run `python scripts/studio.py hook SessionStart` from
the workspace once, since the native start event preceded initialization.
Read `<workspace>/STUDIO.md`, `<workspace>/.codex/docs/runtime.md`, applicable AGENTS.md and rules.
Then read `<workspace>/.agents/skills/day-one-patch/SKILL.md` and follow ALL phases and referenced
files with the user's original arguments, from the workspace root. Do not invoke this wrapper recursively.
Hooks come from the plugin. On clients without hooks, use explicit lifecycle commands.
Roles are in workspace `.codex/agents/*.toml` (legacy registered role configs are also bundled).
If a named role is unavailable, give its full `.md` role contract to a generic child agent;
if no child tools exist, execute sequentially and disclose that limitation.
