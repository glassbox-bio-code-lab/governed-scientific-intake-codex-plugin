---
name: intake-submit
description: Send an existing Glassbox promotion draft through human confirmation and return its receipt.
---

# Submit a saved promotion

When the user asks to send an existing draft, call `submit_promotion(draft_id)`.
Glassbox loads the current saved revision, checks readiness and requests human
confirmation. Never answer the form yourself. Tool arguments are not acceptance.

Present the returned receipt. Resolve relative URLs against the web app base in
[the selected connection](references/ACTIVE_CONNECTION.md). `needs_human_review` means use the Glassbox
`review_url`; `needs_evidence` means saved but not sent. A decline or cancellation
stops this attempt. Do not bypass confirmation or regenerate the draft to submit.
Full provenance, acceptance and the receiver view are in Glassbox. No extra case,
evidence or seal calls are needed to report the returned receipt.

For corrections use `review_promotion` on the same draft. Keep authentication in
the configured transport. Legacy primitives require the explicit advanced profile
and [advanced tool contract](references/tool_contract.md).
