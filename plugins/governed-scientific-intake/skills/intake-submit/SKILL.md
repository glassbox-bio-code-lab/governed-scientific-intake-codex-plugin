---
name: intake-submit
description: Use the Glassbox Bio Codex plugin to send an existing prepared promotion session when the user asks, through actual human confirmation or authenticated browser review, and report its receipt.
---

# Glassbox Bio Governed Promotion Intake — Submit

Use this skill only for an already prepared durable session the user asks to
send. Selection of this skill never stands in for the user's acceptance
of the exact current review. Read [the selected connection](references/ACTIVE_CONNECTION.md),
[shared workflow](references/workflow.md), [tool contract](references/tool_contract.md),
[agent directives](references/AGENTS.md), and [Codex integration notes](references/SKILLS.md).

Retrieve the existing session and show its exact current proposal, blockers,
revision, proposal hash, evidence and independent review plan. If its authority,
contract, evidence or content changed, return to preparation and obtain a fresh
review. Do not create a replacement session or silently edit missing fields.

If `request_intake_confirmation` is advertised and Codex presents its form to the
human, call with current `session_id`, `expected_revision`, `proposal_hash` and a
new `idempotency_key`. Never answer the MCP form yourself. If the tool or form is
unavailable, hand the same session to authenticated browser review. A decline or
cancel stops the attempt; never bypass it through HTTP confirmation.

Inspect the outcome before reporting success. A review link or `needs_evidence`
is not a sent packet. For a submitted case, retrieve `get_case` and
`get_case_seal`, report the actual receipt and signature status, and keep reviewer
approval separate from sending. Preserve project-thread visibility. Never put
credentials or `user_id` in tool arguments, chat or saved content.
