# Parallel teams in Codex

Team workflows use native subagents in one parent session, bounded by the configured concurrency.
Opt in by requesting a team workflow. Partition file ownership and maintain the shared task list
in `production/`; collect artifacts before dependent phases. Do not use Claude team creation,
mailbox or task-list APIs. Communicate through available spawn/message/wait tools. If they are
unavailable, execute roles sequentially and disclose the fallback; independent reviews remain
NOT ASSESSED. All agents inherit the parent sandbox and approvals. Never spawn sidebar chats
as an implementation substitute.
