# Path-specific rules in Codex

Read `.codex/rules/index.md` and load every rule matching a path before reading or changing it.
The `paths:` metadata is interpreted by the studio workflow, not a Codex automatic rule loader.
Files with no paths apply to every task. Nested AGENTS.md files add directory instructions.
Treat rules as guidance; run the validators explicitly if native hooks are unavailable.
Log extra instruction reads with `python scripts/studio.py hook InstructionsLoaded --payload file.json`.

