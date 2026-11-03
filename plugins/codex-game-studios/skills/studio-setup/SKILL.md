---
name: studio-setup
description: Bind this game workspace to installed Codex Game Studios resources without duplicating skills or framework files.
---

Locate this plugin root from this skill path. Run
`python "<plugin-root>/scripts/plugin_workspace.py" init --root "<workspace>"`.
Read the effective AGENTS instruction file, then `<plugin-root>/framework/PLUGIN_RUNTIME.md`.
Run installed `scripts/studio.py doctor` from the workspace. On initial binding run its
`hook SessionStart` once. Follow the installed `<plugin-root>/skills/start/SKILL.md` for onboarding.
Existing configuration is preserved. Do not copy skills, roles, templates or scripts into the workspace.
