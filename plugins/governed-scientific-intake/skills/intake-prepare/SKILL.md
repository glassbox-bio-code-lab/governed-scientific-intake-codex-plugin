---
name: intake-prepare
description: Prepare or revise a durable Glassbox promotion draft through business-level MCP actions.
---

# Prepare a promotion

Call `prepare_promotion` once with the requested receiver, current project,
selected conversation text as `source_context`, and a fresh idempotency key.
Glassbox retrieves requirements and banked material, maps fields, retrieves
approved evidence and saves the draft internally. Pass `banked_item_ids` to
select saved material, or `[]` when only the supplied conversation is intended.
The server cannot read a conversation from the literal words “current conversation”.

Present the returned summary, actual questions and Glassbox `review_url`.
Resolve relative URLs against the web app base in
[the selected connection](references/ACTIVE_CONNECTION.md).
For the user's answers or corrections, call `review_promotion` on that same
`draft_id` with `answers`, `expected_revision` and a new idempotency key.
Reuse the same key and arguments after an uncertain result. Read-only review
needs only `draft_id`; full provenance and acceptance live in Glassbox.

This phase stops at a saved draft. Do not invoke `submit_promotion` unless the
user has asked to send. If sending was already requested, continue to the submit
skill on the same draft. Tool results distinguish saved, failed and submitted.
Keep credentials in the configured transport, outside model-visible arguments.

If only legacy primitives are advertised, this connection uses the advanced
profile. Consult [the advanced tool contract](references/tool_contract.md) only
for that compatibility case. Do not invoke `request_intake_confirmation` during
preparation. Connection troubleshooting is needed only after a connection error.
