# Installed plugin runtime

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
