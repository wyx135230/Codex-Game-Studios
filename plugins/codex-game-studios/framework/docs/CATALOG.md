# Complete catalog / 完整目录

74 migrated workflows plus the plugin-only `$studio-setup` entrypoint.

## Workflows / 工作流

| Skill | Purpose |
| --- | --- |
| [$adopt](<plugin-root>/skills/adopt/SKILL.md) | Brownfield audit — do existing artifacts actually work? Numbered migration plan. Unlike /project-stage-detect, checks compliance not existence. |
| [$architecture-decision](<plugin-root>/skills/architecture-decision/SKILL.md) | Create an ADR documenting a technical decision: context, alternatives considered, consequences. |
| [$architecture-review](<plugin-root>/skills/architecture-review/SKILL.md) | Traceability matrix mapping GDD requirements to ADRs. Finds gaps, cross-ADR conflicts, engine compatibility. PASS/CONCERNS/NOT ASSESSED/FAIL. |
| [$art-bible](<plugin-root>/skills/art-bible/SKILL.md) | Author the Art Bible — visual identity gating asset production. Run before /map-systems. |
| [$asset-audit](<plugin-root>/skills/asset-audit/SKILL.md) | Audit assets against naming conventions, file size budgets, format standards. Finds orphaned assets, missing references. |
| [$asset-spec](<plugin-root>/skills/asset-spec/SKILL.md) | Per-asset visual specs plus AI generation prompts from GDDs and character profiles. After the art bible. |
| [$balance-check](<plugin-root>/skills/balance-check/SKILL.md) | Find balance outliers, broken progressions, degenerate strategies, economy imbalances in formulas and data. 'Check game balance'. |
| [$brainstorm](<plugin-root>/skills/brainstorm/SKILL.md) | Guides the user through finding and choosing a game concept. Use when the user wants game ideas, a new concept, a game jam idea, or to explore other directions, including dropping the current idea and starting over. |
| [$bug-report](<plugin-root>/skills/bug-report/SKILL.md) | Structured bug report from a description, or analyze code for potential bugs. Reproduction steps, severity. |
| [$bug-triage](<plugin-root>/skills/bug-triage/SKILL.md) | Re-evaluate open bugs — priority vs severity, assign to sprints, surface systemic trends. Run when the count grows. |
| [$changelog](<plugin-root>/skills/changelog/SKILL.md) | Auto-generate a changelog from git commits and sprint data. Internal and player-facing versions. |
| [$code-review](<plugin-root>/skills/code-review/SKILL.md) | Architectural code review — coding standards, SOLID, testability, performance concerns. |
| [$consistency-check](<plugin-root>/skills/consistency-check/SKILL.md) | Scan GDDs against the entity registry for cross-document conflicts. Grep-first approach targets conflicting sections, different stats. |
| [$content-audit](<plugin-root>/skills/content-audit/SKILL.md) | Audit GDD content counts against what's implemented — planned vs built. |
| [$create-architecture](<plugin-root>/skills/create-architecture/SKILL.md) | Author the architecture blueprint before code is written. Validates decisions against the pinned engine, flags knowledge gaps. |
| [$create-control-manifest](<plugin-root>/skills/create-control-manifest/SKILL.md) | Builds a short list of must-do and never-do coding rules per system from accepted ADRs. Use when the user wants programmer rules or a cheat sheet from the ADRs, or needs it regenerated after ADR changes. |
| [$create-epics](<plugin-root>/skills/create-epics/SKILL.md) | Turns the GDDs and architecture into epics, one per architectural module. Use when the user wants to break the game into epics or plan the work before writing stories. Not for splitting one epic into stories. |
| [$create-stories](<plugin-root>/skills/create-stories/SKILL.md) | Breaks one epic into implementable stories with acceptance criteria. Use when the user wants stories for an epic or the next batch of work to build. Not for turning the whole design into epics. |
| [$day-one-patch](<plugin-root>/skills/day-one-patch/SKILL.md) | Day-one launch patch — focused fix for known issues found after gold master. Mini-sprint with QA gate and rollback. |
| [$design-review](<plugin-root>/skills/design-review/SKILL.md) | Reviews one design document for completeness, internal consistency, implementability, and design standards. Before handing to programmers. |
| [$design-system](<plugin-root>/skills/design-system/SKILL.md) | Section-by-section GDD authoring for one system — walks through each required section, cross-references dependencies. |
| [$dev-story](<plugin-root>/skills/dev-story/SKILL.md) | Implements one story in code with tests, following its ADRs. Use when the user says to build, implement or start working on a story. Not for checking readiness beforehand or closing the story after. |
| [$estimate](<plugin-root>/skills/estimate/SKILL.md) | Estimate task effort from complexity, dependencies, velocity, risk. Structured estimate with confidence levels. |
| [$gate-check](<plugin-root>/skills/gate-check/SKILL.md) | Ready to advance between development phases? PASS/CONCERNS/NOT ASSESSED/FAIL with blockers and required artifacts. 'Can we move to production?' |
| [$help](<plugin-root>/skills/help/SKILL.md) | What should I do next? Use when stuck or you don't know what to do. |
| [$hotfix](<plugin-root>/skills/hotfix/SKILL.md) | Emergency fix bypassing normal sprint process — hotfix branch, approvals tracked, backport verified, full audit trail. |
| [$launch-checklist](<plugin-root>/skills/launch-checklist/SKILL.md) | Launch readiness across every department: code, content, store, marketing, community, infrastructure, legal, go/no-go sign-offs. |
| [$localize](<plugin-root>/skills/localize/SKILL.md) | Localization pipeline — find hardcoded strings, extract string tables, cultural review, VO, RTL, enforce string freeze. |
| [$map-systems](<plugin-root>/skills/map-systems/SKILL.md) | Decompose a concept into individual systems, map dependencies, prioritize design order, create the systems index. |
| [$milestone-review](<plugin-root>/skills/milestone-review/SKILL.md) | Milestone progress review — completeness, quality metrics, risk, go/no-go recommendation. At checkpoints or before a deadline. |
| [$onboard](<plugin-root>/skills/onboard/SKILL.md) | Onboarding doc for a new contributor or agent — project state, conventions, priorities relevant to the specified role. |
| [$patch-notes](<plugin-root>/skills/patch-notes/SKILL.md) | Player-facing patch notes from git history and changelogs. Translates developer language into player communication. |
| [$perf-profile](<plugin-root>/skills/perf-profile/SKILL.md) | Performance profiling — find bottlenecks, measure against budgets, produce ranked optimization recommendations. |
| [$playtest-report](<plugin-root>/skills/playtest-report/SKILL.md) | Structured playtest report template, or turn existing playtest notes into structured feedback. |
| [$project-stage-detect](<plugin-root>/skills/project-stage-detect/SKILL.md) | Analyze project state, detect stage, identify gaps, recommend next steps. 'Where are we in development?' |
| [$propagate-design-change](<plugin-root>/skills/propagate-design-change/SKILL.md) | Finds architecture decisions (ADRs) made stale by a changed GDD and walks through resolving each. Use when the user changed a number or rule in a GDD and asks which ADRs or architecture decisions are now out of date. |
| [$prototype](<plugin-root>/skills/prototype/SKILL.md) | Concept prototype before GDDs — throwaway HTML, Engine or Paper build, PROCEED/PIVOT/KILL/NOT ASSESSED. After /brainstorm and /setup-engine. |
| [$qa-plan](<plugin-root>/skills/qa-plan/SKILL.md) | QA test plan for a sprint — classifies stories by Logic/Integration/Visual/UI, covers automated tests, manual cases, smoke scope. |
| [$quick-design](<plugin-root>/skills/quick-design/SKILL.md) | Lightweight spec for small changes — tuning adjustments, minor mechanics. Embeds directly into stories; skips full GDD. |
| [$regression-suite](<plugin-root>/skills/regression-suite/SKILL.md) | Map test coverage to GDD critical paths, find fixed bugs lacking regression tests, flag drift from new features. |
| [$release-checklist](<plugin-root>/skills/release-checklist/SKILL.md) | Pre-release checklist — build verification, certification requirements, store metadata, launch readiness. |
| [$retrospective](<plugin-root>/skills/retrospective/SKILL.md) | Sprint or milestone retrospective from completed work, velocity, blockers. Actionable insights for the next iteration. |
| [$reverse-document](<plugin-root>/skills/reverse-document/SKILL.md) | Generate missing design or architecture docs from existing implementation — works backwards from code and prototypes. |
| [$review-all-gdds](<plugin-root>/skills/review-all-gdds/SKILL.md) | Holistic cross-GDD review — contradictions between systems, dominant strategies, economic imbalance, cognitive overload, pillar drift. |
| [$scope-check](<plugin-root>/skills/scope-check/SKILL.md) | Scope creep check — current scope versus the original plan. Flags additions, quantifies bloat, recommends cuts. 'Any scope creep?' |
| [$security-audit](<plugin-root>/skills/security-audit/SKILL.md) | Security audit — save tampering, cheat vectors, network exploits, data exposure, input validation. Before public or multiplayer release. |
| [$settings](<plugin-root>/skills/settings/SKILL.md) | View or change project config — effective merged values, or set locally in project.local.yaml. |
| [$setup-engine](<plugin-root>/skills/setup-engine/SKILL.md) | Configure engine and version. Pins it in AGENTS.md; WebSearch fills reference docs when the version is beyond LLM training data. |
| [$skill-improve](<plugin-root>/skills/skill-improve/SKILL.md) | Improve a skill via a test-fix-retest loop — static checks, targeted fixes, keep or revert on score change. |
| [$skill-test](<plugin-root>/skills/skill-test/SKILL.md) | Validate skill files for structural compliance and behavioral correctness. Four modes: static linter, spec, category rubric, audit. |
| [$smoke-check](<plugin-root>/skills/smoke-check/SKILL.md) | Critical-path smoke gate before QA hand-off — runs the automated suite. A failed check means the build is not QA-ready. |
| [$soak-test](<plugin-root>/skills/soak-test/SKILL.md) | Soak test protocol for extended play — what to observe and log for slow leaks, fatigue, late-appearing edge cases. |
| [$sprint-plan](<plugin-root>/skills/sprint-plan/SKILL.md) | New or updated sprint plan from the current milestone, completed work, and available capacity. |
| [$sprint-status](<plugin-root>/skills/sprint-status/SKILL.md) | Fast, concise sprint snapshot — burndown and emerging risks for situational awareness. 'How is the sprint going?' |
| [$start](<plugin-root>/skills/start/SKILL.md) | Guides a first-time user through onboarding and picks the right workflow. Use when the user is new, just cloned or installed the studio, has no idea or engine yet, asks where to begin, or wants to bring in an existing game. |
| [$story-done](<plugin-root>/skills/story-done/SKILL.md) | Closes a finished story: verifies each acceptance criterion, checks for design or ADR deviations and updates its status. Use when the user says a story is done, finished or ready to close. |
| [$story-readiness](<plugin-root>/skills/story-readiness/SKILL.md) | Checks whether a story is ready to implement: clear acceptance criteria, no open questions, valid ADR and dependencies. Use when the user asks if a story, or the sprint's stories, are ready to start or build. |
| [$team-audio](<plugin-root>/skills/team-audio/SKILL.md) | Orchestrate the audio team — audio-director, sound-designer, technical-artist, gameplay-programmer — direction through implementation. |
| [$team-combat](<plugin-root>/skills/team-combat/SKILL.md) | Orchestrate the combat team — game-designer, gameplay-programmer, ai-programmer, technical-artist, sound-designer, qa-tester — design through implement and validate. |
| [$team-level](<plugin-root>/skills/team-level/SKILL.md) | Orchestrate the level team — level-designer, narrative-director, world-builder, art-director, systems-designer, qa-tester — for complete area creation. |
| [$team-live-ops](<plugin-root>/skills/team-live-ops/SKILL.md) | Orchestrate the live-ops team — live-ops-designer, economy-designer, analytics-engineer, community-manager, writer — for a season or live event. |
| [$team-narrative](<plugin-root>/skills/team-narrative/SKILL.md) | Orchestrate the narrative team — narrative-director, writer, world-builder, level-designer — for story, world lore, narrative-driven levels. |
| [$team-polish](<plugin-root>/skills/team-polish/SKILL.md) | Orchestrate the polish team — performance-analyst, technical-artist, sound-designer, qa-tester — to optimize and harden a feature or area. |
| [$team-qa](<plugin-root>/skills/team-qa/SKILL.md) | Orchestrate the QA team through a full testing cycle — qa-lead strategy and test plan, qa-tester case writing, execution, sign-off. |
| [$team-release](<plugin-root>/skills/team-release/SKILL.md) | Orchestrate the release team — release-manager, qa-lead, devops-engineer, producer — to execute a release from candidate to deployment. |
| [$team-ui](<plugin-root>/skills/team-ui/SKILL.md) | Orchestrate the UI team through the UX pipeline — authoring, visual design, implementation, review, polish. Uses /ux-design, /ux-review, studio templates. |
| [$tech-debt](<plugin-root>/skills/tech-debt/SKILL.md) | Track, categorize and prioritize technical debt across the codebase — scans for debt indicators, maintains a register. |
| [$test-evidence-review](<plugin-root>/skills/test-evidence-review/SKILL.md) | Quality review of test files and evidence — goes beyond existence, evaluates assertion coverage. ADEQUATE/INCOMPLETE/MISSING/NOT ASSESSED per story. |
| [$test-flakiness](<plugin-root>/skills/test-flakiness/SKILL.md) | Find flaky tests from CI logs — aggregates pass rates, spots intermittent failures, recommends quarantine. After multiple runs. |
| [$test-helpers](<plugin-root>/skills/test-helpers/SKILL.md) | Generate engine-specific test helper libraries — assertion utilities, factory functions, mocks in the engine's test folder. Reduces boilerplate. |
| [$test-setup](<plugin-root>/skills/test-setup/SKILL.md) | Scaffold the test framework and CI — tests/ directory, engine test runner, GitHub Actions workflow. Once, before the first sprint. |
| [$ux-design](<plugin-root>/skills/ux-design/SKILL.md) | Section-by-section UX spec authoring for a screen, flow or HUD. Reads the player journey to provide context; also project-wide accessibility. |
| [$ux-review](<plugin-root>/skills/ux-review/SKILL.md) | Validate a UX spec, HUD design or pattern library — accessibility, GDD alignment, readiness. APPROVED / NOT ASSESSED / NEEDS REVISION / MAJOR REVISION NEEDED. |
| [$vertical-slice](<plugin-root>/skills/vertical-slice/SKILL.md) | Pre-production validation — end-to-end build to confirm the full loop is achievable before committing to Production. After GDDs, architecture, UX specs. |

## Roles / 角色

| Role | Purpose |
| --- | --- |
| [accessibility-specialist](<plugin-root>/framework/.codex/agents/accessibility-specialist.toml) | Accessibility standards and assistive features — remapping, text scaling, colorblind modes, screen reader support. |
| [ai-programmer](<plugin-root>/framework/.codex/agents/ai-programmer.toml) | Implements game AI — behavior trees, state machines, pathfinding, perception, decision-making, NPC and enemy behavior, AI debugging. |
| [analytics-engineer](<plugin-root>/framework/.codex/agents/analytics-engineer.toml) | Telemetry and analytics — event tracking, player behavior, A/B test frameworks, dashboard specification, data pipelines. |
| [art-director](<plugin-root>/framework/.codex/agents/art-director.toml) | Owns visual identity — style guides, art bible, asset standards, color palettes, UI visual direction. |
| [audio-director](<plugin-root>/framework/.codex/agents/audio-director.toml) | Owns sonic identity — music direction, sound palette, audio implementation strategy, mix balance. |
| [community-manager](<plugin-root>/framework/.codex/agents/community-manager.toml) | Player-facing communication — patch notes, social posts, community updates, feedback collection, player bug triage, crisis communication. |
| [creative-director](<plugin-root>/framework/.codex/agents/creative-director.toml) | Highest creative authority — vision, tone, aesthetic direction. Use when a decision affects game identity or department leads deadlock. |
| [devops-engineer](<plugin-root>/framework/.codex/agents/devops-engineer.toml) | Build pipelines, CI/CD configuration, version control workflow, branching strategy, automated test pipelines, deployment infrastructure. |
| [economy-designer](<plugin-root>/framework/.codex/agents/economy-designer.toml) | Resource economies — loot tables, sink/faucet analysis, progression curve calibration, economic balance. |
| [engine-programmer](<plugin-root>/framework/.codex/agents/engine-programmer.toml) | Core engine systems — rendering pipeline, physics, memory, resource loading, scene management, performance-critical framework code. |
| [game-designer](<plugin-root>/framework/.codex/agents/game-designer.toml) | Mechanical and systems design — core loops, progression, combat, economy, player-facing rules. Mechanics-level questions. |
| [gameplay-programmer](<plugin-root>/framework/.codex/agents/gameplay-programmer.toml) | Implements designed mechanics as code — player systems, combat, interactive features, gameplay system code. |
| [godot-csharp-specialist](<plugin-root>/framework/.codex/agents/godot-csharp-specialist.toml) | Godot 4 C# quality — .NET patterns, attribute-based exports, signal delegates, async patterns, type-safe node access. |
| [godot-gdextension-specialist](<plugin-root>/framework/.codex/agents/godot-gdextension-specialist.toml) | Native code integration with Godot — GDExtension API, godot-cpp and godot-rust bindings, custom node types, the native boundary. |
| [godot-gdscript-specialist](<plugin-root>/framework/.codex/agents/godot-gdscript-specialist.toml) | GDScript code quality — static typing enforcement, signal architecture, coroutine patterns, GDScript idioms, typed and performant. |
| [godot-shader-specialist](<plugin-root>/framework/.codex/agents/godot-shader-specialist.toml) | Godot rendering customization — shading language, visual shaders, material setup, particle shaders, post-processing. |
| [godot-specialist](<plugin-root>/framework/.codex/agents/godot-specialist.toml) | Authority on Godot-specific patterns and APIs — node/scene architecture, signals, resources; guides GDScript vs C# vs GDExtension. |
| [lead-programmer](<plugin-root>/framework/.codex/agents/lead-programmer.toml) | Lead programmer — code-level architecture, coding standards, code review, API design, refactoring strategy, assigning work to specialist programmers. |
| [level-designer](<plugin-root>/framework/.codex/agents/level-designer.toml) | Spatial design for levels and areas — encounter layouts, pacing, difficulty, layout planning, environmental storytelling. |
| [live-ops-designer](<plugin-root>/framework/.codex/agents/live-ops-designer.toml) | Post-launch content — seasonal events, battle passes, content cadence, retention, engagement analytics. Keeps the game fresh. |
| [localization-lead](<plugin-root>/framework/.codex/agents/localization-lead.toml) | Internationalization architecture — i18n system design, string extraction workflows, locale testing, locale-specific issues, translation pipeline. |
| [narrative-director](<plugin-root>/framework/.codex/agents/narrative-director.toml) | Story architecture, world-building, character design, dialogue strategy. Narrative structure and direction rather than writing individual lines. |
| [network-programmer](<plugin-root>/framework/.codex/agents/network-programmer.toml) | Multiplayer networking — state replication, lag compensation, matchmaking, network protocol, netcode and bandwidth optimization. |
| [performance-analyst](<plugin-root>/framework/.codex/agents/performance-analyst.toml) | Performance analyst — profiling, bottlenecks, memory analysis, frame time investigation, recommends optimizations, tracks metrics over time. |
| [producer](<plugin-root>/framework/.codex/agents/producer.toml) | Production concerns — sprint planning, milestone tracking, risk, scope, cross-department coordination when multiple departments must synchronize. |
| [prototyper](<plugin-root>/framework/.codex/agents/prototyper.toml) | Throwaway builds — concept prototypes after brainstorm to test an idea is fun before GDDs; vertical slices pre-production. Speed over standards. |
| [qa-lead](<plugin-root>/framework/.codex/agents/qa-lead.toml) | Test strategy and process — test plan creation, bug severity assessment, regression planning, release quality gates, readiness evaluation. |
| [qa-tester](<plugin-root>/framework/.codex/agents/qa-tester.toml) | Writes test cases, bug reports, and checklists — test case generation, regression checklist creation, execution documentation. |
| [release-manager](<plugin-root>/framework/.codex/agents/release-manager.toml) | Release pipeline — certification checklists, store submissions and page prep, platform requirements, version numbering, release-day coordination. |
| [security-engineer](<plugin-root>/framework/.codex/agents/security-engineer.toml) | Protects against cheating, exploits, breaches — anti-cheat measures, secure save data and network comms, player privacy compliance. |
| [sound-designer](<plugin-root>/framework/.codex/agents/sound-designer.toml) | SFX specifications and spec sheets — audio event documentation, mixing parameters, sound category definitions. |
| [systems-designer](<plugin-root>/framework/.codex/agents/systems-designer.toml) | Detailed subsystem mechanics — combat formulas, progression curves, crafting recipes, status effect interactions, mathematical modeling of a mechanic. |
| [technical-artist](<plugin-root>/framework/.codex/agents/technical-artist.toml) | Technical artist bridging art and engineering — shaders, VFX, rendering optimization, art pipeline tools, art-to-engine issues. |
| [technical-director](<plugin-root>/framework/.codex/agents/technical-director.toml) | High-level technical decisions — engine architecture, technology choices, performance strategy, technical risk, cross-system conflicts. |
| [tools-programmer](<plugin-root>/framework/.codex/agents/tools-programmer.toml) | Internal dev tools — editor extensions, content authoring tools, debug utilities, pipeline automation, editor workflow. |
| [ue-blueprint-specialist](<plugin-root>/framework/.codex/agents/ue-blueprint-specialist.toml) | Blueprint architecture and Blueprint/C++ boundary — optimization, maintainable graphs. Prevents Blueprint spaghetti, enforces clean BP patterns. |
| [ue-gas-specialist](<plugin-root>/framework/.codex/agents/ue-gas-specialist.toml) | Gameplay Ability System — abilities, gameplay effects, attribute sets, tags, ability tasks, prediction. Prevents common GAS anti-patterns. |
| [ue-replication-specialist](<plugin-root>/framework/.codex/agents/ue-replication-specialist.toml) | Unreal networking — property replication, RPCs, client prediction, relevancy, net serialization, bandwidth. Server-authoritative architecture. |
| [ue-umg-specialist](<plugin-root>/framework/.codex/agents/ue-umg-specialist.toml) | Unreal UI implementation — UMG widget hierarchy, data binding, CommonUI input routing, widget styling, UI optimization. |
| [ui-programmer](<plugin-root>/framework/.codex/agents/ui-programmer.toml) | Implements user interface systems — menus, HUDs, inventory screens, dialogue boxes, UI framework code, screen flow. |
| [unity-addressables-specialist](<plugin-root>/framework/.codex/agents/unity-addressables-specialist.toml) | Unity asset management — Addressable groups, loading/unloading, content catalogs, remote delivery, asset bundle optimization, fast load times. |
| [unity-dots-specialist](<plugin-root>/framework/.codex/agents/unity-dots-specialist.toml) | Unity Data-Oriented Technology Stack — Entity Component System, Jobs, Burst compiler optimization, hybrid renderer, correct ECS patterns. |
| [unity-shader-specialist](<plugin-root>/framework/.codex/agents/unity-shader-specialist.toml) | Unity rendering — Shader Graph, custom HLSL, VFX Graph, render pipeline customization (URP/HDRP), post-processing within performance budgets. |
| [unity-specialist](<plugin-root>/framework/.codex/agents/unity-specialist.toml) | Authority on Unity-specific patterns and APIs — guides MonoBehaviour vs DOTS/ECS, Unity subsystems including Addressables and Input System. |
| [unity-ui-specialist](<plugin-root>/framework/.codex/agents/unity-ui-specialist.toml) | Unity UI implementation — UI Toolkit (UXML/USS), UGUI Canvas, data binding, runtime UI performance, cross-platform adaptation. |
| [unreal-specialist](<plugin-root>/framework/.codex/agents/unreal-specialist.toml) | Authority on Unreal-specific patterns and APIs — guides Blueprint vs C++, UE subsystems (GAS, Enhanced Input, Niagara, etc.). |
| [ux-designer](<plugin-root>/framework/.codex/agents/ux-designer.toml) | User experience flows, interaction design, information architecture — user flow mapping, interaction pattern design, onboarding, accessibility requirements. |
| [world-builder](<plugin-root>/framework/.codex/agents/world-builder.toml) | World builder for lore — factions, cultures, history, geography, ecology, world rules. Faction design, lore consistency checks. |
| [writer](<plugin-root>/framework/.codex/agents/writer.toml) | Writer of player-facing text — dialogue, lore entries, item and ability descriptions, environmental text. |

## Helpers / 辅助工具

Run shell helpers with `python <plugin-root>/scripts/studio.py run <basename> [arguments]` or directly with Bash.

- `adr-dep-graph.sh`
- `adr-status.sh`
- `agent-check.sh`
- `artifact-check.sh`
- `asset-scan.sh`
- `bug-stats.sh`
- `code-markers.sh`
- `compat-inventory.sh`
- `config-set.sh`
- `content-count.sh`
- `debt-register.sh`
- `flaky-stats.sh`
- `gdd-structure-check.sh`
- `godot-parse-check.gd`
- `hook-input.sh`
- `inputs-check.sh`
- `md-section.sh`
- `migrate-v1-config.sh`
- `plan-math.sh`
- `project-coherence.sh`
- `project-state.sh`
- `read-guard.sh`
- `registry.sh`
- `review-receipts.sh`
- `review-scope.sh`
- `rotate-session-state.sh`
- `session-state.sh`
- `set-stage.sh`
- `skill-lint.sh`
- `story-facts.sh`
- `story-status.sh`
- `test-run.sh`
- `test-scaffold.sh`
- `write-guard.sh`
- `yaml-get.awk`
