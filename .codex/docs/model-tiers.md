# Model tiers in Codex

All workflows and roles inherit the selected Codex session model. Original skill model aliases
are recorded in `.codex/compat/skill-metadata/` for migration auditing only. They do not switch
models or determine price. For simple read/format work use a suitable accessible model; for
implementation use the normal coding model; for cross-document gates use adequate reasoning.
Configure a supported custom agent `model` and `model_reasoning_effort` only deliberately.
