---
name: studio-setup
description: Initialize a writable game workspace using the complete Codex Game Studios plugin template.
---

Locate this plugin root from this skill file. Use the workspace already selected in Codex;
ask for a directory only if none is known. Run `python "<plugin-root>/scripts/plugin_workspace.py"
init --root "<workspace>"`. Read the result and preserved-file list, then read workspace
STUDIO.md, AGENTS.md and .codex/docs/runtime.md. Run `python scripts/studio.py doctor` from
the workspace. If newly initialized, run `python scripts/studio.py hook SessionStart` once.
Read and follow .agents/skills/start/SKILL.md for onboarding. All 74 original
workflows are available; consult docs/CATALOG.md. No network service or API key is required
by this plugin beyond the normal Codex sign-in. Existing project files are preserved.
