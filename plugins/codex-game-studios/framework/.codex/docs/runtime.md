# Codex runtime contract

This file takes precedence over inherited platform-specific examples in the migrated references.
User instructions and host sandbox policy always take precedence over studio conventions.

## Skills and tools

Invoke repository skills as `$start`, `$dev-story`, etc., or ask in natural language.
Historical `/name` examples mean the skill of that name, not a new built-in Codex slash command.
Read the named SKILL.md and its referenced files; never assume a Claude Skill tool exists.
`$ARGUMENTS` means the user's invocation arguments. `STUDIO_SKILL_DIR` is a convention,
not an injected variable: resolve it to `<plugin-root>/skills/<name>` if encountered.
Run every configuration command shown at the start of a skill BEFORE its phases, from
the repository root. Codex does not execute `!` backtick injection syntax.
`Read`, `Glob`, `Grep`, `Write`, `Edit`, `Bash` and `AskUserQuestion` in references describe
operations: use available file/search/shell/apply_patch/question tools. Use `rg` for search.
For a required user decision, ask in chat and wait if no question tool is available.
Do not repeat an approval already granted for the current scope; prepare the concrete draft first.

## Roles and delegation

Native role definitions are `<plugin-root>/framework/.codex/agents/<name>.toml`. Their `.md` siblings preserve
the original role contract for inspection, scripts, and older clients.
Use the available spawn tool with that role. If named custom agents are unavailable,
spawn a generic worker with the COMPLETE role body and relevant runtime/rules instructions.
If spawning itself is unavailable, perform role steps sequentially and mark that fallback.
Do not claim independent review when the same agent performs both steps.
Skill `context: fork` metadata means run that skill as a bounded child task and await its result;
without spawning, run it sequentially with a separate artifact/report.
Delegate only when the user or the selected workflow calls for it. Preserve director → lead →
specialist hierarchy, independent-task parallelism, boundaries, named outputs and escalation.
Subagents report questions to the parent; the parent puts required decisions to the user.
They inherit parent permissions. Original `tools`, `allowed-tools`, `disallowedTools`,
`maxTurns`, `memory` and model aliases are preserved in compatibility metadata, not asserted
as Codex enforcement. Keep tool scope and turn budget in the brief and track it there.
Persistent role memory is ordinary project data in `.studio/agent-memory/<role>/MEMORY.md`;
read it on demand and write only within the authorized task. No implicit memory injection.

At the start of a role task, read `<plugin-root>/framework/.codex/compat/agent-metadata/<role>.yaml`.
Apply its tool scope and `maxTurns` as task-budget instructions (not sandbox guarantees).
For every skill in its `skills:` list, read `<plugin-root>/skills/<name>/SKILL.md` and the
relevant references as preloaded procedural guidance; do not start unrelated workflows.
If `memory: project` is present, read `.studio/agent-memory/<role>/MEMORY.md` when it exists
and maintain it within the authorized task. Ignore the recorded Anthropic model alias.

## Models

All agents inherit the user's selected Codex model. There are no Anthropic model aliases
or automatic per-skill model switches. The original low/standard/deep tiers remain advisory.
Choose a supported model in the client or set native agent model fields deliberately if desired.
Never promise cost savings or a capability based on the original model tier.

## Rules and lifecycle

At session start read `production/session-state/active.md` if present and the shared
coordination/coding references linked by AGENTS.md. Read `<plugin-root>/framework/.codex/rules/index.md`, then load
each rule whose globs match any file you will touch. Nested AGENTS.md applies by directory.
`paths:` in the migrated rule files is routing metadata, not a native Codex rule loader.
Hooks require a trusted project and explicit hook trust in clients that support hooks.
`<plugin-root>/framework/.codex/hooks.json` delegates native events to `<plugin-root>/scripts/studio.py`; it normalizes shell and
multi-file apply_patch payloads, calls the original validators and forwards their decisions.
PermissionRequest triggers the old permission notification; Stop triggers idle/completion
notification. Instruction-load logging is explicit (not a native event): log shared guidance
on start via the lifecycle command, and invoke `hook InstructionsLoaded` for additional reads.
Use `python <plugin-root>/scripts/studio.py hook SessionStart` at startup if native hooks are unavailable,
`hook PreCompact` before a planned context reset, and `hook Stop` before finishing. Payload
can be supplied with `--payload file.json` for all events. For manual tool checks use the
documented payload shapes and invoke PreToolUse / PostToolUse around the operation.
Read guards require a Read payload; native shell reads cannot always be recognized.
Never treat hooks as a sandbox: shell writes, external editors and specialized tools can bypass
file-level validators. Apply the same rules and run helpers explicitly in these cases.
Read/write warnings remain advisory where upstream made them advisory; validator denial blocks.

## Configuration and results

Preserve project.yaml resolution, local overrides, legacy mirrors, rigor expansion, automation
modes, evidence hashes, checkpoint recovery and all domain checks. Helpers emit observations,
not pass/fail verdicts; inspect their rows. Engine validation needs the chosen engine executable.
Keep unknown/missing evidence as NOT ASSESSED. No commits, pushes or publication without user
instruction. Upstream updates are opt-in and refer to the original source; never install them
directly over this Codex port. Use the import manifest to review and reapply compatible changes.
