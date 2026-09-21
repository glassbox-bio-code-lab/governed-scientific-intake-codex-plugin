---
name: intake
description: Use the Governed Scientific Intake Codex plugin to retrieve a receiving contract, prepare or correct a scientific handoff, request user confirmation, report its receipt, or inspect its project history through the configured local MCP server.
---

# Governed Scientific Intake for Codex

This is the compatibility entrypoint for older prompts. For new work use
`$intake-prepare` to make or revise a draft and `$intake-submit` only when the
user asks to send an existing session. Selection of a skill is not confirmation.

Read [the shared workflow](references/workflow.md), [tool contract](references/tool_contract.md),
and [agent directives](references/AGENTS.md) before preparing or sending a packet.
These preserve the universal skill's provenance, accountability, independent-review
and history rules. Use [Codex integration notes](references/SKILLS.md) for client
behavior; read [connection instructions](references/CONNECTION.md) for setup/errors.

Read [the selected connection](references/ACTIVE_CONNECTION.md) before using tools or opening links.
Use this plugin's configured HTTP MCP tools. Credentials belong in transport
configuration: never place a password, token or `user_id` in a tool argument,
message, attachment or saved content. Do not switch to legacy stdio authentication,
register a duplicate MCP server, or reconstruct the packet through shell/REST calls.

Prepare a durable intake, show the server's exact review and collect unresolved
human answers. When the user asks to send, invoke `request_intake_confirmation`
if available; the human answers the Codex form. Do not answer an MCP elicitation
or approval form yourself. Never call an HTTP confirmation endpoint as a bypass.
If the tool or form is unavailable, or it returns `needs_human_review`, open the
existing authenticated browser review. An explicit decline/cancel ends the attempt.

Report the actual saved/sent state using `get_case` and `get_case_seal`, without
claiming unsigned or merely signed records were verified. Use `get_project_thread`
for history, preserving filtered visibility and independently required reviews.
Do not use reviewer or contract-governance mutations for this sender workflow.

For material the user wants to save before promotion, use the companion `intake-bank`
skill. To prepare from banked material, verify the explicitly selected draft first;
local categories/readiness never establish approved evidence or human confirmation.
Resolve the receiving contract and server project before creating an intake session.
