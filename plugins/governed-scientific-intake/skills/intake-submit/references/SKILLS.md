# Codex plugin integration notes

This is the Codex desktop/CLI adapter for the universal governed intake workflow.
The plugin has an `intake` entrypoint for server workflows and a separate
`intake-bank` skill for local saved drafts. Saving to the bank never submits anything. Its workflow, tool contract and agent directives are bundled copies
of the canonical universal references.

## Tools and state

Use the tools supplied by this plugin's MCP server, matching discovered names if
Codex adds a namespace. Follow [workflow.md](workflow.md) and
[tool_contract.md](tool_contract.md) for requests and response nesting. Keep returned
sessionId/revision/proposalHash, caseId and request idempotency keys in task context.
Do not replace a missing value with a guessed identifier. Append relative UI paths
to the web app base in [ACTIVE_CONNECTION.md](ACTIVE_CONNECTION.md), preserving any
base path. The MCP endpoint does not serve review pages. A profile switch starts
a new task; do not reuse session/case identifiers from another deployment.

The native HTTP connection reads the endpoint-specific `GSI_MCP_TOKEN_<connection hash>`
variable supplied by the credential launcher. Connection setup manages its name.
The legacy tool schema may still show `user_id`; leave it out. Hosted identity is
bound to the transport. Do not read credentials with shell tools or print them.
For `agent_context`, `agentPlatform: "codex"` is descriptive; other metadata must
come from known facts and cannot change the authenticated actor.

## Approval in the app or CLI

The optional `request_intake_confirmation` must be checked in tool
inventory. Calling it opens an MCP user form; a conversational "yes" does not
replace that form response. The assistant must not select its own confirmation.

If the tool is missing, the client cannot render a form, or it returns
`needs_human_review`, show/open the server's browser-review link. If it returns
`confirmation_declined` or `confirmation_cancelled`, stop. Do not silently change
clients or invoke REST confirmation to obtain a different outcome. Some clients
may decline an unsupported form; diagnose that and let the user choose browser
review rather than retrying automatically. The form is client-mediated, not proof
of human identity beyond the authenticated client.

When switching account tokens, start a fresh connection/task. Server sessions are
bound to the initializing credential; another token cannot resume that transport.
The persisted intake remains accessible only to its authorized owner.

## Delivery and history

Surface the server receipt and actual case/seal state, including `needs_evidence`,
unsigned or unavailable seals. `get_case_seal` may generate a current export; it
does not verify it. Use `get_project_thread` for status/history requests. Additional
reviewers remain independent even if the user confirms sending once.
