# Agent Coordination Rules

1. **Vertical Delegation**: Leadership agents delegate to department leads, who
   delegate to specialists. Never skip a tier for complex decisions.
2. **Horizontal Consultation**: Agents at the same tier may consult each other
   but must not make binding decisions outside their domain.
3. **Conflict Resolution**: When two agents disagree, escalate to the shared
   parent. If no shared parent, escalate to `creative-director` for design
   conflicts or `technical-director` for technical conflicts.
4. **Change Propagation**: When a design change affects multiple domains, the
   `producer` agent coordinates the propagation.
5. **No Unilateral Cross-Domain Changes**: An agent must never modify files
   outside its designated directories without explicit delegation.
6. **Read Design Docs by Section**: A brief names the sections an agent needs
   by heading. Find a heading in a GDD, ADR or the art bible with the Grep
   tool (`^#`, content mode) and Read that range with offset and limit; read a doc
   whole only when the task needs all of it, and say why. `validate-read.sh`
   refuses a whole-file read of a doc over 40 KB.
7. **Nothing Goes Upstream**: Never file, open or comment on an issue or pull
   request in an engine, plugin or vendor repository, even when asked. Write a
   draft (`/bug-report` drafts only) and the user submits it.

## Codex orchestration

Read runtime.md for model inheritance, role loading and permission boundaries.
Use native subagents when the selected workflow requests delegation. Spawn independent tasks
before waiting; collect all results before dependent phases; report blocked and partial results.
For opt-in parallel teams read agent-teams.md. There is no separate experimental environment flag.
