# Governed Intake Tool Contract

This reference describes MCP input names and response shapes. All examples omit
credentials and use illustrative scientific-review fixture identifiers. Resolve
real contract/project/field identifiers from the user's authorized workspace.
Read the server's discovered schemas if they differ from these examples.

## Authentication and naming

Streamable HTTP MCP authenticates `Authorization: Bearer ...` outside tool
arguments. The Codex plugin uses this transport and must omit `user_id`.
Universal local stdio clients retain the legacy `user_id` argument, whose value
is an opaque account-session credential (or seeded token only in explicit pilot
mode), not a username. Bind it through the platform's private credential handling;
do not ask for or display it in chat. REST uses `x-api-key` and an optional
matching `x-user-id`. Do not forward an MCP bearer-header convention to REST.

MCP request keys are snake_case, including `agent_context`, `contract_id` and
`session_id`; response keys often use camelCase (`agentContext`, `contractId`,
`sessionId`). `caller`/`agent_context` cannot grant authority. Only supply known
platform metadata; never fabricate a user identity or workstation.

## retrieve_intake_contract

Retrieve before completing. The returned effective contract always includes the
centrally owned universal envelope. Receiver and workflow definitions are additive
layers recorded in `promotionLayers`; field `sourceContract` identifies the layer
that owns its evidence scope. Supply an optional registered receiving team as
`submission.receiver` and preserve it when starting completion. Without published
requirements for that receiver, the server selects `universal-promotion`; without
a receiver it can use governance intake. Explicit receiver selection cannot
bypass that team's published requirements. For a named receiver, `list_contracts`
can identify an authorized overlay. Unresolved receiver-contract ambiguity returns
`status: confirmation_required`, `contract: null`; ask for selection and retrieve
again with `contract_id`. Do not guess or call completion until resolved.

<!-- mcp: retrieve_intake_contract -->
```json
{
  "submission": {"text": "Scientific summary of a formulation experiment.", "project": "PRJ-ONCO-27"},
  "contract_id": "scientific-review",
  "attachments": [{"name": "notes.txt", "content": "Supplied observations, including uncertainty."}],
  "agent_context": {"agentPlatform": "codex"}
}
```

The result supplies `contract`, optional `classification`, and
`gatekeeper.nextRecommendedTool`. Do not assume a field is populated without
checking `status`. For current shared-session state:

<!-- mcp: retrieve_intake_contract -->
```json
{"session_id": "INTAKE-returned-by-server"}
```

This returns `{status, session, reviewUrl, contract, ...}`. `session.proposal`
contains the current snapshot; it may be null while unresolved or failed.

## complete_intake_details

Start a durable shared session by including `idempotency_key` and no `session_id`.
`title` and `submission` are required tool arguments. Omitting the key selects a
legacy completion response rather than the durable-session workflow.

<!-- mcp: complete_intake_details -->
```json
{
  "title": "Scientific review handoff",
  "submission": {"text": "Scientific summary of a formulation experiment.", "project": "PRJ-ONCO-27", "fieldValues": {}},
  "contract_id": "scientific-review",
  "attachments": [{"name": "notes.txt", "content": "Supplied observations, including uncertainty."}],
  "idempotency_key": "unique-start-key"
}
```

Returns the session directly: `sessionId`, `revision`, `status`, `proposal`,
`proposalHash`, `blockers`, `reviewUrl`. Fields/evidence/claims/classification and
review plan live under `proposal`. `review_ready` can still contain blockers.
Legacy completion instead returns a wrapper with `proposal` and `pendingFields`;
do not mistake that response for a saved session.

Only UTF-8 text attachments are supported: txt, md, csv, json, tsv, xml, yaml,
yml; at most ten files, one million characters per file and two million combined
input/answer characters. Message text is bounded to 100,000 characters. Do not
silently drop unsupported material or claim a binary PDF was uploaded.

Follow up using the returned revision and actual contract field IDs:

<!-- mcp: complete_intake_details -->
```json
{
  "title": "",
  "submission": {"text": "Here is my corrected summary.", "fieldValues": {"sci.summary": "My corrected scientific summary."}},
  "session_id": "INTAKE-returned-by-server",
  "expected_revision": 1,
  "idempotency_key": "unique-followup-key"
}
```

A follow-up contract selection uses `contract_id` on this call. Attachments are
accepted only at session start. To read without adding a message, use
`retrieve_intake_contract(session_id=...)`, or send `title: ""`, `submission: {}`,
and `session_id` to completion, omitting `idempotency_key` and `contract_id`.

## request_intake_confirmation (optional)

Available only when the connected server advertises it. Use only with a client
that presents MCP forms to the human. Substitute the current returned
revision/hash exactly:

<!-- mcp: request_intake_confirmation -->
```json
{
  "session_id": "INTAKE-returned-by-server",
  "expected_revision": 1,
  "proposal_hash": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "idempotency_key": "unique-confirmation-key"
}
```

No approval boolean belongs in these arguments. The server presents the saved
proposal and original material to the client; only the human answers its `confirm`
form field. An accepted form is checked against current authority, contract,
evidence, revision and hash. Completion is not rerun.

Success returns the session directly with `status: submitted`, `caseId`,
`confirmation`, receiver/review plan and (on receipt-enabled servers) `receipt`.
`needs_evidence` means the case was saved but NOT sent; open its record URL.
Unsupported clients or previews over 60,000 characters return
`{status: needs_human_review, session, reviewUrl}`. Decline/cancel returns the same
wrapper with `confirmation_declined`/`confirmation_cancelled`. Do not automatically
retry an explicit denial. A missing/stale/blocked input is an error, not approval.
Retry an uncertain successful call only with its original revision/hash/key.

## submit_intake_submission_for_review

This legacy tool always returns a human-review handoff. It ignores supplied
`field_decisions`; it cannot confirm or submit a session. Use it to obtain the
browser fallback URL, including when the optional confirmation tool is absent.

<!-- mcp: submit_intake_submission_for_review -->
```json
{"title": "", "session_id": "INTAKE-returned-by-server"}
```

The result is `{status: needs_human_review, session, reviewUrl, ...}`. For an
existing legacy case, send `title: ""` and `case_id` instead; its URL is
`/cases/{caseId}/review`. Never omit both session and case IDs when intending to
resume an existing record. Without either, a supplied submission creates a new
legacy case. Do not pass human decisions expecting that tool to apply them.

`update_field_decision`, `submit_packet`, and `resubmit_case` also retain their
schemas but return review handoffs without applying sender decisions. A rejected
field remains unresolved until replaced by a confirmed/edited decision in the
application. Never use REST confirmation as a workaround.

## get_case and get_case_seal

After receiving a case ID, retrieve the persisted result:

<!-- mcp: get_case -->
```json
{"case_id": "CASE-returned-by-server"}
```

Preserve `primaryReceiver`, `sensitivityFlags`, `requiredAdditionalReviews`,
`reviewPlan`, `lifecycleStatus` and `submittedAt`. Required reviews are independent.
Sending is not approval. A saved `needs_evidence` case has not been sent.

<!-- mcp: get_case_seal -->
```json
{"case_id": "CASE-returned-by-server"}
```

This returns a current seal record including `signature_status`, or an error.
It may generate an audit export. State signed/unsigned/unavailable accurately;
`get_case_seal` is not cryptographic verification. A receipt's `verificationUrl`
is a place to check the signature, not evidence that checking already succeeded.

## get_project_thread

After a case ID exists, use for its associated project history, routing status
and timeline questions:

<!-- mcp: get_project_thread -->
```json
{"case_id": "CASE-returned-by-server"}
```

The backend filters unauthorized items. Preserve each returned item's `visibility`
object when displaying or forwarding content. Do not reconstruct missing items or
probe alternate endpoints to evade the filter. Resolve relative UI URLs against
the configured web-app origin (Codex local default: http://127.0.0.1:5173).
