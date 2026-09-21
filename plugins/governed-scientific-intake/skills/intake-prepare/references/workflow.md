# Shared governed intake workflow

These rules apply to both the universal agent skill and the Codex plugin. The
platform entrypoint determines connection setup and whether a genuine user-facing
MCP form is available. Read [tool_contract.md](tool_contract.md) for request shapes
and [AGENTS.md](AGENTS.md) for authority and provenance boundaries.

## Retrieve and prepare

1. Retrieve the effective promotion contract with `retrieve_intake_contract`,
   preserving the user's text, authorized project, optional `submission.receiver`
   and supported attachments. Every packet includes the universal promotion
   envelope; published receiver requirements and optional workflow requirements
   are additive layers. A registered receiver without a contract can receive a
   universal packet; an unselected receiver defaults to governance intake. Use
   `list_contracts` to resolve additional published requirements when necessary. `confirmation_required` means no contract was
   selected: show the authorized choices, collect a selection or clarification,
   and retrieve again. Do not invent the route or silently substitute a contract.
2. Start a durable session with `complete_intake_details`: include `title`,
   `submission.text`, the user's authorized `submission.project`, the returned
   `contract_id`, and a fresh `idempotency_key`. Text attachments use `name` and
   `content`. Only direct human answers belong in `submission.fieldValues`.
   Preserve the selected `submission.receiver` when starting the session. The
   backend classifies, retrieves permitted evidence, and proposes completion.
   Ask explicitly for the eight required promotion declarations:
   `promotion.contextOfUse`, `promotion.aiRoleIdentity`,
   `promotion.dataEvidence`, `promotion.relianceConsequence`,
   `promotion.humanOversight`, `promotion.assessmentStatus`,
   `promotion.limitationsRestrictions`, and `promotion.accountabilityChanges`.
   Each requires explicit, human-confirmed text. There are no automatic
   `unknown` or `none` defaults: an accountable submitter must explicitly
   declare an unknown. Keep the upstream scientific-model declaration separate
   from server-observed packet-preparation provider and run metadata. Never
   invent upstream history, model performance, evidence validity, or regulatory
   suitability.
3. Keep the returned `sessionId`, `revision`, `proposalHash`, and `reviewUrl`.
   Completion returns a session directly; retrieval with `session_id` wraps it
   under `session`. Values are in `proposal.suggestions`, unresolved issues in
   `blockers`; legacy completion uses `pendingFields` instead. Never infer a
   successful submission from a tool name or from `review_ready` alone.
4. Show `promotionLayers` with their versions and the effective contract, primary route, sensitivity flags, full
   review plan and all additional reviews. Present field values with their exact
   statuses, sources, confidence, citations and visibility. Group them as user
   supplied, approved-source retrieved, inferred, conflicting/unsupported, and
   missing. Show uncertainty; citations establish provenance, not scientific truth.
5. Ask only for unresolved answers or corrections. Never invent human rationale,
   AI contribution, inventorship, patent sensitivity, or decision-support claims.
   Send follow-ups with `title: ""`, `session_id`, current `expected_revision`, a
   fresh `idempotency_key`, and `submission.text` and/or `submission.fieldValues`.
   Field keys must come from the returned contract. New attachments cannot be
   added to a session after its start; do not silently create a replacement intake.
   Reread the updated proposal before seeking approval.

## Resolve state and uncertain outcomes

| Server state/result | Required next action |
|---|---|
| `needs_contract` / retrieval `confirmation_required` | Ask for contract selection; preserve any existing session. |
| `processing` | Retrieve the same session later; do not start another intake. |
| `failed` | Show the returned error and preserve the session. Resolve the cause; a user-directed follow-up may retry preparation. |
| `review_ready` with blockers | Collect missing answers/conflict resolution and send a revision-bound follow-up. |
| `review_ready` without blockers | Present the complete review and request the supported user confirmation. |
| `needs_human_review` | Open the authenticated review URL; this is not submission. |
| `confirmation_declined` / `confirmation_cancelled` | Stop this submission attempt. Do not auto-retry or switch to an API bypass. |
| `needs_evidence` | A case was saved but not sent. Open its record/review URL and complete evidence there. |
| `submitted` | Retrieve the saved case and report its receipt and routing, not receiver approval. |

If a start call has an uncertain outcome before a session ID is returned, retry
only the identical start payload and original idempotency key. Once its ID is
known, retrieve that session. For an uncertain follow-up, retrieve first and use
the identical request/key if a retry is needed. Never reuse a key for changed
content. For an uncertain confirmation, retrieve first; a retry of the identical
revision/hash/key is safe, but an explicit decline or cancel is not an uncertain
outcome. A new attempt after rejection requires a new user instruction.

## Confirm and send

After the user asks to send, retrieve the current session and show the review.
Use `request_intake_confirmation` only if the server advertises it AND the client
can present its form to the human user. Supply the current `session_id`,
`expected_revision`, `proposal_hash`, and a new `idempotency_key`. This call asks
for approval; it is not itself proof of approval. Do not answer an MCP elicitation
or approval form yourself. The server sends the stored proposal and original
material, then reauthenticates and checks current contract/evidence and the exact
revision before atomically saving/submitting. Do not pass `confirm`, decisions,
or edited fields as tool arguments. The `confirm` form field belongs to the human.

This is client-mediated confirmation, not independent proof of human presence.
If the tool is absent, the client cannot show forms, or the tool returns
`needs_human_review` (including an oversized preview), use authenticated browser
review. Obtain the link with `submit_intake_submission_for_review(title="",
session_id=...)` when needed. That legacy tool never applies `field_decisions`.
Never call an HTTP confirmation endpoint as a bypass for a missing or declined
MCP form. An explicit approval or capability error must not be treated as consent.
If revision/hash/contract/evidence changed, refresh the review and collect fresh
approval; never merely update the hash and claim the old approval still applies.

## Receipt, independent reviews and history

For a returned case ID, use `get_case` and `get_case_seal`. Preserve any session
`receipt` (case ID, record URL, verification URL and `sealStatus`) and distinguish
saved/not-sent, sent-for-review, and reviewer-approved states. `signed` is not
`verified`; `unsigned` and `unavailable` must be stated accurately. A seal read
can create/read a current audit export; it is not a receipt proving the human
reviewed or the receiving party approved the science. Do not claim independent
verification unless a verification result for the relevant package was obtained.

Keep `primaryReceiver`, `sensitivityFlags`, `requiredAdditionalReviews`,
`reviewPlan`, and `lifecycleStatus` separate. Every required review-plan entry is
completed by its authorized reviewer; do not collapse multiple reviews into one.
Do not invoke reviewer approval/rejection, contract publication, assignment,
archival or other governance mutations as part of a sender intake request.

Once a case ID exists, use `get_project_thread(case_id=...)` for its associated
project history and status instead of reconstructing a timeline from chat memory. Preserve each item's `visibility` and
the server's filtering. Resolve relative review/record/verification paths against
the configured web-app origin, not the MCP origin. Never put credentials in URLs.

## Existing legacy cases

Resume an existing case with `get_case`/`get_project_thread`; do not create a
session just to resubmit it. Legacy `update_field_decision`, `submit_packet`,
`resubmit_case`, and `submit_intake_submission_for_review` are browser-review
handoffs. Their retained decision parameters are ignored. A `rejected` field
remains pending until the human replaces it with a confirmed or edited decision
in the application. Preserve the original case ID and its review URL.

## Returned requirements

A receiver may return a submitted packet with additional named requirements.
These are case-specific amendments with reviewer attribution, not automatic
changes to a published contract. Preserve the return history, collect the missing
answers and obtain fresh human confirmation. Repeated requests may recommend an
overlay change to its owner; the recommendation does not publish or grant policy.

## Universal promotion sections

Use the eight sections below as an organizing lens over the required universal
fields. They are not a second contract and do not add defaults:

| Section | Required universal field and declaration |
| --- | --- |
| `contextOfUse` | `promotion.contextOfUse`: intended question, receiving workflow, audience, decision boundary, conditions, and unsupported uses. |
| `aiRoleIdentity` | `promotion.aiRoleIdentity`: upstream scientific/AI tool and known version, exact contribution, or explicitly declared unknown history. |
| `dataEvidence` | `promotion.dataEvidence`: supplied material, source references and versions, permissions, processing, supporting evidence, and gaps. |
| `relianceConsequence` | `promotion.relianceConsequence`: intended reliance relative to other evidence, possible consequence, uncertainty, and escalation boundary. |
| `humanOversight` | `promotion.humanOversight`: reviewers, actual checks and corrections, unresolved questions, and decisions requiring a responsible human or receiver. |
| `assessmentStatus` | `promotion.assessmentStatus`: known assessment/testing status, available results, and what remains unestablished; receiver requirements carry detailed plans, results, and suitability when needed. |
| `limitationsRestrictions` | `promotion.limitationsRestrictions`: limitations, restrictions, exclusions, uncertainty, sensitivity, and prohibited or unsupported uses. |
| `accountabilityChanges` | `promotion.accountabilityChanges`: accountable sender and receiver, relevant versions, changes, and renewed-review needs. |

The submit attestation records human review and responsibility for the packet;
it does not validate the upstream model or scientific content. The server's
observed provider, model, run, source retrieval, and validation records remain
provenance facts, not replacements for the user's upstream declaration. See
`docs/reference/FDA_EMA_PROMOTION_MAPPING.md` for the FDA/EMA-informed mapping
and its non-regulatory boundaries.


### Shared packet attestation

The web review and MCP confirmation form show the same server-owned, versioned
packet attestation, including that confirmation does not establish model
validity or suitability. For browser/API hosts, direct submit and resubmit
require the accepted `attestationVersion` from `case.submissionAttestation`
after displaying its text. This is not permission for an agent to manufacture
human acknowledgement: agents must continue using client-mediated confirmation
or the authenticated review URL. Each send binds the actor, record version and
reviewed content hash; previous receipts remain in confirmation history.
Current effective receiving requirements are rechecked before promotion.
