# Contributing

Keep all 74 workflows and 49 role contracts accounted for when changing the port.
Read `AGENTS.md`, `<plugin-root>/framework/.codex/docs/runtime.md` and applicable domain rules first.
Run `python -m unittest discover -s tests -v`, `python scripts/verify.py`, then
`python scripts/build_plugin.py` after changing packaged content.

Edit source files in this repository, not generated `plugins/codex-game-studios/` or
the user's installed plugin cache. Verify install/uninstall with an isolated `--home`.
Do not add secrets, personal settings, session logs or game project data to plugin archives.
Preserve the upstream MIT license and update docs/CATALOG.md when adding workflows.

`scripts/migrate_source.py` is a maintenance importer; it refuses existing targets by default.
`--overwrite-imported` deliberately replaces imported content and requires reapplying port
adaptations. Review the source hashes and diffs before using it. Do not run it as an updater
inside an active game project. The generated plugin is local/private distribution material;
public directory submission is a separate task.
