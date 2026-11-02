# Runtime boundaries

The plugin runs local Python and Bash helpers in the game workspace. Review and trust
the packaged hooks in Codex before enabling them. It does not add a network service,
collect credentials or require a separate API key. Upstream update checks are off by default.

Studio rules and hooks are workflow guardrails. They do not replace the Codex sandbox,
OS file permissions or engine-editor protections. Shell writes and some specialized tool
paths may bypass file-level hooks; run the corresponding validators explicitly.

The installer merges one marketplace entry and appends one marked config block. Its
uninstaller checks the exact owned target before deletion, refuses modified config blocks,
and preserves game workspaces and unrelated plugins. Back up project data using your usual
version-control process. Do not package `.env`, tokens, personal configuration or session data.

Report issues privately to your distribution maintainer; no upstream issue is submitted
automatically. Keep a reproduction and redact credentials before sharing diagnostic output.
