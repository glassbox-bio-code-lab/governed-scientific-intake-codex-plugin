---
name: intake-prepare
description: Use the Glassbox Bio Codex plugin to retrieve a receiving contract and prepare or revise a durable scientific promotion draft. Stop before human confirmation or submission.
---

# Glassbox Bio Governed Promotion Intake — Prepare

Read [the selected connection](references/ACTIVE_CONNECTION.md) and use this
plugin's authenticated HTTP MCP tools. Follow [the shared workflow](references/workflow.md),
[tool contract](references/tool_contract.md), [agent directives](references/AGENTS.md),
and [Codex integration notes](references/SKILLS.md). Read [connection guidance](references/CONNECTION.md)
when configuring or diagnosing access. Discover actual tools and contracts.

Retrieve the effective receiver contract and authorized project, then prepare or
revise a durable session with an idempotency key. Preserve the user's original
material, provenance, session ID, revision, proposal hash, review URL and all
unresolved questions. If using `intake-bank`, verify the selected local draft and
treat it as unverified source material. Present the exact server proposal with
blockers, source statuses and required reviews.

This phase stops at a saved draft. Do not invoke `request_intake_confirmation`,
`submit_intake_submission_for_review`, sender decision tools or HTTP confirmation.
If the user wants to send the prepared session, use `$intake-submit` with that same
session. Never place a password, token or `user_id` in arguments, chat or saved
content. Do not register a duplicate MCP server or substitute legacy stdio.
