# Migration contract / 迁移对照

The imported template is a local file snapshot, not a checkout with verified upstream commit history. Source hashes are recorded in `migration-manifest.json`. All 638 source files have mapped targets. Historical product documents remain under `upstream/` and do not define the supported Codex install procedure.

| Original mechanism | Codex implementation | Boundary |
| --- | --- | --- |
| Root and nested CLAUDE.md | Root and nested AGENTS.md, explicit referenced-file reads | No automatic `@` expansion |
| 74 .claude/skills workflows | 74 .agents/skills workflows; plugin entrypoints bootstrap and read them | Original phases and reference assets retained |
| 49 Markdown agents | Native standalone TOML plus legacy registered role configs | Inherit selected Codex model and permissions |
| Agent tool / teams | Native spawn/message/wait tools with full-role fallback | Sequential fallback explicitly disclosed |
| model aliases | Session model inheritance; original metadata in compat | No fabricated model equivalence or pricing claims |
| allowed-tools / maxTurns / memory | Scope and budget in task brief; explicit project memory | Workflow constraints, not an OS sandbox |
| Skill shell injection | Explicit configuration command before workflow phases | No hidden environment substitution |
| Path rules | Explicit rule routing index and nested AGENTS.md | Match rules before touching new or existing files |
| settings.json hooks | Native hooks.json and Python event adapter | Requires project/plugin hook trust |
| Write/Edit hooks | apply_patch reconstruction, including multi-file and moves | Shell writes need explicit helper checks |
| Bash / PowerShell guards | Normalized command payloads, original validators and deny contract | Not a complete shell parser or sandbox |
| SessionStart / Stop / PreCompact | Native adapter or manual lifecycle commands | Stop adapter runs synchronously |
| Notifications | PermissionRequest and completion mapped to notification helper | Windows notification UI; see platform note below |
| InstructionsLoaded | Explicit instruction-load logging | No claim of native automatic instruction event |
| statusLine command | `python <plugin-root>/scripts/studio.py status` | Uses available payload data; no custom desktop status-bar injection |
| worktree include list | Explicit local-preference copy guidance | Not assumed to be automatically loaded by Codex |
| Engine helpers, registry, evidence | Original deterministic helpers with migrated paths | Engine binaries and actual test frameworks still required |
| Upstream updater | Preserved, disabled by default and pointed to real upstream | Never automatically install Claude updates over this port |

## Tool adapter examples

For a pending shell command, save this JSON and run `python <plugin-root>/scripts/studio.py hook PreToolUse --payload payload.json`:

```json
{"tool_name":"exec_command","tool_input":{"cmd":"git status --short"}}
```

For a native patch:

```json
{"tool_name":"apply_patch","tool_input":{"command":"*** Begin Patch\n*** Add File: src/example.txt\n+example\n*** End Patch\n"}}
```

For a bounded read:

```json
{"tool_name":"Read","tool_input":{"file_path":"design/gdd/combat.md","offset":1,"limit":100}}
```

Native hook input fields and plain stdout handling differ from the original runtime. The adapter reconstructs prospective file content, calls the retained scripts, forwards exit-2 denials, and aggregates model-visible context as native JSON. Original advisory checks remain advisory. Unknown or malformed patch input fails with an explanation instead of silently skipping checks.

## Plugin/workspace separation

The plugin root contains portable `plugin.json`, a `.codex-plugin/plugin.json` compatibility overlay, 75 skill entrypoints, hook registration, runtime scripts and the complete migrated `template/`.

From version 0.1.1, the native single-plugin ZIP excludes custom installer scripts. It includes declared square SVG logo/composer icons and can be selected through the desktop archive-upload entrypoint. A separate marketplace ZIP has `.agents/plugins/marketplace.json` and `plugins/codex-game-studios/`; extract that ZIP and add its root directory as a marketplace. Its root has no project hooks. The optional compatibility installer remains in the source repository only.

`plugin_workspace.py init` creates only missing files in the selected project. It never overwrites existing game files. `.studio/installation.json` records files created by setup and marks the workspace for plugin hook dispatch. Workspace `STUDIO.md` exposes the studio instructions when an existing AGENTS.md is preserved. The plugin skips unrelated projects and distinct nested Git repositories. It does not copy project hooks.json, avoiding duplicate hook registration.

Native roles are copied into the workspace because plugins are not assumed to register custom agents automatically. New clients discover standalone definitions; legacy project configuration registers role files. With existing incompatible configuration, workflows use the documented generic-worker fallback instead of replacing the project's configuration.

Installation preserves the personal marketplace name and other entries. Uninstallation removes only its own exact marketplace entry, marked config block and owned source directory. It preserves all game workspaces and Codex's shared caches. Review the plugin in Codex's native UI if cached installation state remains.

## Verification scope

`verification.json` contains observed check results. No engine is selected in the template; a missing engine or unrun review remains NOT ASSESSED. Automated structural checks do not establish that every LLM-mediated workflow produces correct game design or code. Native UI installation, hook trust and full engine integration require target-client acceptance testing.

## Official references

- [Plugin packaging and local marketplaces](https://developers.openai.com/plugins/build/plugins)
- [Skill discovery](https://developers.openai.com/codex/skills)
- [Custom subagents](https://developers.openai.com/codex/subagents)
- [Hook payloads and trust](https://learn.chatgpt.com/docs/hooks)
- [Desktop plugin deep links](https://learn.chatgpt.com/docs/app/commands)
