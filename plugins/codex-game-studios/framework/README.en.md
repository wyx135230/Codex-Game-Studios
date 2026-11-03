# Codex Game Studios

[中文](README.md) · [Complete catalog](docs/CATALOG.md) · [Migration notes](docs/MIGRATION.md)

A local Codex desktop and CLI plugin, adapted from [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios). It includes **74 workflows, 49 specialist roles, 35 helper files and 14 domain rule sets** for Godot, Unity and Unreal. The plugin adds one onboarding skill, `$studio-setup`.

This is a game development studio template and toolset. Your game code, designs and production records live in your workspace.

## Native plugin installation (recommended)

Requirements: Python 3.11+, Git, and a local Codex client. On Windows, install Git for Windows to provide Git Bash. No additional Python packages or separate plugin API key are required.

### Option 1: Upload plugin archive

In Codex desktop, choose **Add → Upload plugin archive**, then select `dist/codex-game-studios-0.2.0.zip` directly. Do not extract it or run an installer. Complete the client import/install prompts, then run `$studio-setup` in a new chat in your game workspace.

The single-plugin ZIP has `plugin.json`, `.codex-plugin/plugin.json`, `skills/`, `hooks/`, `assets/`, `scripts/` and shared resources in `framework/` at its root. It contains 75 skill entrypoints, 49 roles and all migrated workflows.

### Option 2: Add plugin marketplace

Extract `dist/codex-game-studios-marketplace-0.2.0.zip`. Open **Add → Add plugin marketplace** and fill its three text fields:

| Field | Local installation on this machine |
| --- | --- |
| Source | `E:\Users\LENOVO\Documents\ChatGPT\Codex-Game-Studios\dist\codex-game-studios-marketplace` |
| Git ref | Leave empty; not used for a local directory |
| Sparse paths | Leave empty; not used for a local directory |

Click **Add marketplace**, then install Codex Game Studios from the catalog. If extracted elsewhere, paste that directory's actual absolute path into Source. It must directly contain `.agents/plugins/marketplace.json`. Do not enter the ZIP, the JSON file itself, or the plugin subdirectory.

The built source directory is `dist/codex-game-studios-marketplace/`. Its root has no project `<plugin-root>/framework/.codex/hooks.json`; adding this catalog does not initialize a game project.

To install directly from GitHub without downloading a ZIP, use:

| Field | Git installation |
| --- | --- |
| Source | `wyx135230/Codex-Game-Studios` or `https://github.com/wyx135230/Codex-Game-Studios.git` |
| Git ref | `main`, or empty for the default branch |
| Sparse paths | Prefer empty for a full checkout; optionally enter both paths below, one per line |

```text
.agents/plugins
plugins/codex-game-studios
```

Sparse checkout must include both the marketplace catalog and its referenced plugin directory. The dialog's default-branch and `plugins/codex` placeholder text is not a required value.

```bash
codex plugin marketplace add wyx135230/Codex-Game-Studios --ref main --sparse .agents/plugins --sparse plugins/codex-game-studios
```

CLI users can run `codex plugin marketplace add <absolute-marketplace-directory>`, then install through `/plugins`. The marketplace ZIP must be extracted and added as a catalog; upload the separate single-plugin ZIP through the archive uploader.

Review and trust hooks when prompted. Setup binds the workspace without copying skills, roles, templates or common scripts. Existing project configuration is preserved. The plugin requires local execution in Codex desktop/CLI. Private installation is separate from public directory submission; public submissions currently cannot contain lifecycle hooks.

Packaging follows the [official guide](https://developers.openai.com/plugins/build/plugins) and [icon requirements](https://developers.openai.com/plugins/deploy/submission#icons-and-screenshots). Offline validation and CLI registration do not establish that the desktop upload UI has been exercised.

### Optional: source-repository compatibility installer

Native installation does not require these scripts, and they are excluded from the standard ZIP. From the source repository on Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

This builds the package when necessary. From the source repository on macOS/Linux, or without opening a desktop link:

```bash
python3 scripts/plugin_manager.py install
```

The installer copies the plugin to `~/.codex/plugins/local-source/codex-game-studios`, adds its entry to `~/.agents/plugins/marketplace.json`, and appends a marked enable block to your Codex user configuration. Other plugins, model settings and authentication remain intact. Reinstalling reports `already-installed`.

The Windows launcher opens the plugin detail link. Restart Codex desktop and look under **Plugins → Local Game Studios → Codex Game Studios**. If your personal marketplace already exists, its original name is preserved. Complete any client installation prompts and review/trust the hooks. Start a new chat in your game workspace and run:

```text
$studio-setup
```

Codex requires explicit trust for plugin hooks. The installer does not bypass that requirement. Installation does not modify your game project. Setup only binds configuration and a short instruction bridge. Existing instructions are preserved outside the marked plugin section.

In the CLI, use `/plugins` to select the local marketplace. CLI plugin subcommands vary by release; the installed CLI 0.125 only exposes `plugin marketplace`, so these scripts do not depend on the newer `codex plugin add` command.

## Uninstall, disable and upgrade

For archive-upload or marketplace installations, use **Disable** or **Uninstall** on the Codex plugin detail page. No uninstall script is required. Update by uploading the newer single-plugin ZIP or refreshing the marketplace source through the client.

The following scripts apply only to the optional source compatibility installer.

From the source repository:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\uninstall.ps1
```

On other platforms use `python3 scripts/plugin_manager.py uninstall`. This removes the owned plugin source, marketplace entry and marked configuration block. Restart Codex afterwards. **Game workspaces, source code, design documents and session data are preserved.** If Codex still shows a cached installed entry, uninstall it through its plugin detail page. The script does not recursively delete shared Codex caches.

You can also disable or uninstall through the desktop plugin page. For script installations, run the uninstall script to remove the local source registration as well. To upgrade: uninstall the old package, extract the new version and install it. Run `$studio-setup` from the new plugin to refresh the binding. Project artifacts remain intact; preview legacy cleanup before applying it.

`python scripts/plugin_manager.py status` reports local source state. `--home <directory>` selects an isolated user home containing `.codex` and `.agents`, useful for testing. If the marked configuration block has been manually changed, uninstall stops with an explanation rather than deleting edited settings.

## 0.2.0: installed resources, minimal workspaces

The plugin `skills/` directory contains all 74 full workflows and references, plus onboarding. Roles, rules, templates and helpers remain in plugin `framework/`. There is no second skill library in the game workspace.

Initial setup of a new project creates only:

```text
AGENTS.md                    # Short plugin instruction bridge
project.yaml                 # Game configuration
.studio/installation.json    # Binding, version and ownership record
```

If `AGENTS.override.md` exists, update that effective instruction file instead. Existing instructions are retained outside the marked studio section; existing project.yaml is preserved. Setup creates no STUDIO.md, .agents/skills, project .codex directory, shared scripts, README, license or GitHub configuration copies, and no directory links.

Game designs, code, assets, tests, engine references and production records are created only by workflows that need them. Mutable legacy preferences and role memory use `.studio/technical-preferences.md` and `.studio/agent-memory/` when needed. Hooks may write project session records.

Use plugin-owned role contracts and compatibility metadata with generic child agents if named roles are unavailable. No per-project copies of 49 agent configurations are generated. Disclose sequential fallback when child-agent tools are unavailable.

For a 0.1.x workspace, run `$studio-setup` from the updated plugin, then preview cleanup:

```bash
python "<plugin-root>/scripts/plugin_workspace.py" cleanup --root "<game-directory>"
python "<plugin-root>/scripts/plugin_workspace.py" cleanup --root "<game-directory>" --apply
```

Only unchanged, ledger-owned skill/framework files, studio tests, common runtime scripts and old STUDIO.md are eligible. Edited files, role memory and game artifacts stay. Other categories such as old README copies stay too. Without ownership records nothing is guessed or recursively removed.

Uninstalling retains game artifacts; plugin workflows require reinstalling/enabling the plugin. Setup or a trusted plugin hook refreshes the binding when a host update moves its versioned cache.

## Use the repository as a project template

Open this repository in Codex desktop, or run `codex` from its root, then:

```bash
python <plugin-root>/scripts/studio.py doctor
```

Ask Codex to run `$start`. Root `AGENTS.md` provides project guidance; `<plugin-root>/skills/` contains workflows and `<plugin-root>/framework/.codex/agents/` contains native roles. The default `<plugin-root>/framework/.codex/config.toml` uses role registration verified with CLI 0.125. `<plugin-root>/framework/.codex/config.modern.toml` is provided for newer standalone-agent clients; do not apply it blindly to an older CLI.

Choose either the plugin or the direct project template. Plugin workflows and references run from the installed package. The source-template mode keeps its local workflow library for development; the plugin does not copy that library into games.

## From concept to release

| Goal | Example skills |
| --- | --- |
| Start or adopt a project | `$start`, `$onboard`, `$adopt`, `$reverse-document` |
| Select engine and pin version | `$setup-engine`: Godot 4, Unity, Unreal 5, engine-specific source and test roots |
| Concept and design | `$brainstorm`, `$quick-design`, `$design-system`, `$art-bible`, `$ux-design` |
| Systems and architecture | `$map-systems`, `$create-architecture`, `$architecture-decision`, `$architecture-review` |
| Plan and implement | `$create-epics`, `$create-stories`, `$story-readiness`, `$dev-story`, `$story-done` |
| Specialist collaboration | `$team-combat`, `$team-ui`, `$team-level`, `$team-narrative`, other team workflows |
| Tests and review | `$test-setup`, `$smoke-check`, `$regression-suite`, `$code-review`, `$gate-check` |
| Production and release | `$sprint-plan`, `$milestone-review`, `$release-checklist`, `$launch-checklist`, `$hotfix` |
| Maintain the studio | `$settings`, `$skill-test`, `$skill-improve`, `$help` |

See the [catalog](docs/CATALOG.md) for all 74 workflows and 49 roles. Historical `/name` examples refer to workflow names; invoke them as `$name` or use natural language. They are not additional built-in Codex slash commands.

Example: `$dev-story production/epics/epic-01/story-01.md`. Roles retain the director → lead → specialist hierarchy, output boundaries and escalation rules. Workflows delegate when subagent tools are available. If named roles are unavailable, pass the complete role contract to a generic child agent. If no subagent tools exist, execute sequentially and disclose the fallback; do not claim independent review.

## Configuration and runtime behavior

`project.yaml` stores engine, stage and workflow settings; `project.local.yaml` holds personal overrides. The original configuration precedence, legacy stage mirrors, rigor expansion, automation modes and system overrides are retained through `<plugin-root>/framework/.codex/hooks/yaml-helper.sh resolve_config`.

```text
$settings modes.rigor=standard
$settings --local modes.automation=guided
```

All roles inherit the selected Codex model. Original Anthropic aliases and tool metadata remain under `<plugin-root>/framework/.codex/compat/` for auditing; they do not imply automatic model switches, tool isolation or enforced turn limits. Tool scope, budgets and project memory are handled in workflow briefs and the runtime contract.

In plugin mode a short project AGENTS bridge reads `.studio/installation.json` and the installed `framework/PLUGIN_RUNTIME.md`; rules stay under plugin `framework/.codex/rules/`. Source-template mode still uses `<plugin-root>/framework/.codex/docs/runtime.md` and `<plugin-root>/framework/.codex/rules/index.md`. Claude-style `@` imports, automatic path-rule loading and skill shell injection have been converted into explicit reads and commands.

Session recovery reads `production/session-state/active.md`. The adapter preserves commit checks, registry protection, write guards, asset checks, bounded-read checks, agent logs and artifact validation. Codex `apply_patch` additions, updates, deletions, moves and multi-file patches are checked per file.

Without native hooks, use explicit lifecycle commands. These examples are for source-template mode; in plugin mode use the installed studio.py absolute path and run from the game workspace:

```bash
python <plugin-root>/scripts/studio.py hook SessionStart
python <plugin-root>/scripts/studio.py hook PreCompact
python <plugin-root>/scripts/studio.py hook Stop
python <plugin-root>/scripts/studio.py status
```

For tool checks use `hook PreToolUse --payload payload.json` and `hook PostToolUse --payload payload.json`; see [migration notes](docs/MIGRATION.md). Hooks are guardrails: shell file operations, external editors and specialized tool paths still require explicit workflow checks.

## Verify and build

Run these commands from the source repository root. Bound game workspaces use the installed `<plugin-root>/scripts/studio.py doctor`; framework tests stay in the source repository.

```bash
python -m unittest discover -s tests -v
python <plugin-root>/scripts/studio.py doctor
python scripts/verify.py
python scripts/build_plugin.py
python scripts/validate_distribution.py
```

Git Bash must be allowed to start on Windows. Set `STUDIO_BASH` if automatic discovery fails. Results go to `docs/verification.json`. `scripts/probe_codex.py` checks CLI parsing with isolated temporary configuration and leaves personal settings unchanged.

Distribution checks use the development dependency PyYAML (`python -m pip install PyYAML`); the installed plugin uses only the standard library. Building produces the single-plugin upload ZIP, standalone marketplace directory, marketplace ZIP and SHA-256 sidecars.

Checks cover source-file accounting, role and skill structure, patch conversion, denial/context forwarding, isolated installation/uninstallation, shell syntax and representative retained helpers. **The complete model-driven workflows, actual desktop UI installation clicks and game-engine builds have not been exercised.** They require the target client, account and chosen engine.

If skills are missing, restart the client and check that the plugin is enabled. If hooks do not run, review hook trust. Install Git for Windows if Bash is missing. Existing global configuration errors must be corrected at the location reported by Codex; this plugin does not rewrite model or service-tier settings.

## Provenance and license

The supplied upstream template contains 638 files and identifies itself as version 1.2.0. The [migration manifest](docs/migration-manifest.json) records source paths, targets and source SHA-256 hashes. Historical README, changelog and upgrade notes are under `docs/upstream/`; use this README and the runtime contract for Codex operations. The original [MIT license](LICENSE) is preserved.

Packaging follows official [plugin](https://developers.openai.com/plugins/build/plugins), [skill](https://developers.openai.com/codex/skills), [subagent](https://developers.openai.com/codex/subagents) and [hook](https://learn.chatgpt.com/docs/hooks) documentation. This is a local plugin without a hosted service or public directory publication.
