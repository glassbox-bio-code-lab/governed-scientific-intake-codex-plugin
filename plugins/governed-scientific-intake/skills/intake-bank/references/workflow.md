# Save now, prepare later

Resolve `BANK_TOOL` to this skill's actual `scripts/bank.py` path. Resolve `BANK_ROOT`
to a stable workspace's `.intake-bank` or the user's chosen directory. Use these
exact paths across later tasks; never silently switch to another bank. The helper
uses the Python standard library and POSIX file locks (Linux/macOS).

## Initialize and save

```bash
python3 "$BANK_TOOL" --bank "$BANK_ROOT" init --project "Formulation study"
python3 "$BANK_TOOL" --bank "$BANK_ROOT" add \
  --title "Assay results, run 4" --kind result --origin user-supplied \
  --file "/absolute/path/results.csv" --file "/absolute/path/lab-notes.pdf" \
  --description "Preliminary; repeat experiment pending" --tag formulation \
  --request-id save-run-4
```

The project label is a local organizational label, not a server project ID. Source
files are copied, never moved or modified. Any format can be stored, up to 128 MiB
per file and 50 supplied files per item. Later MCP upload eligibility is narrower.
The default status is `draft`; the helper records byte hashes, original names,
resolved source paths and capture time. It does not assert who authored a file.

For selected conversation text, pass content through stdin, preserving it exactly.
Use a quoted heredoc delimiter or a file/structured process API so shell syntax in
scientific text cannot execute. Do not interpolate content into a shell command.

```bash
python3 "$BANK_TOOL" --bank "$BANK_ROOT" add \
  --title "Proposed explanation" --kind note --origin agent-generated \
  --description "Working hypothesis; not established" --stdin --request-id save-hypothesis-1 <<'BANK_NOTE'
The selected tentative explanation goes here, preserving qualifications.
BANK_NOTE
```

Kinds: `work`, `document`, `evidence`, `result`, `note`. Origins: `user-supplied`,
`agent-generated`, `external`, `derived`. Choose based on known context. A supplied
external paper remains external; do not claim the user authored it. Add a DOI/URL or
known source reference with `--source-uri`. This records a reference without
fetching it. Preserve supplied evidence IDs/versions in the saved JSON/document or
description; their validity must be checked later with the receiving service.

An uncertain save can be replayed with identical content, metadata and request ID.
The helper returns the same item; reuse with different content fails. Without a
request ID, inspect the bank before retrying. Do not silently create duplicates.

## Find, inspect and revise

```bash
python3 "$BANK_TOOL" --bank "$BANK_ROOT" list --query formulation
python3 "$BANK_TOOL" --bank "$BANK_ROOT" show ITM_RETURNED_ID
python3 "$BANK_TOOL" --bank "$BANK_ROOT" verify
python3 "$BANK_TOOL" --bank "$BANK_ROOT" update ITM_RETURNED_ID --status ready
python3 "$BANK_TOOL" --bank "$BANK_ROOT" update ITM_RETURNED_ID --status excluded
```

Replace illustrative IDs with the complete returned IDs. `list` searches titles,
descriptions and tags; `show` checks item file hashes and returns its metadata.
Read a saved file only as needed for the user's task. `verify` checks indexed item
bytes and reports unindexed directories after an interrupted save; it never adopts
or deletes them automatically. These are consistency checks, not digital signatures.

Statuses are local planning labels: `draft`, `ready`, `excluded`. No status means
scientifically validated, human-attested, submitted or reviewer-approved. Metadata
updates retain before/after history. File content and original provenance are not
edited by the helper. To correct content, save a new item with `--supersedes OLD_ID`;
the old snapshot stays available. Deliberately exclude an obsolete version if it
should no longer be considered. No automatic deletion or remote synchronization.

## Build a selected draft

```bash
python3 "$BANK_TOOL" --bank "$BANK_ROOT" prepare \
  --title "Formulation review draft" --item ITM_FIRST_ID --item ITM_SECOND_ID
python3 "$BANK_TOOL" --bank "$BANK_ROOT" verify-packet PKT_RETURNED_ID
```

The selected items become a new packet snapshot. It includes all their copied
files, original provenance, an inventory and an overview. Selection does not change
item statuses. Excluded items cannot be selected. Existing packets are not rewritten
when the bank changes; description changes or current exclusion block later handoff
verification so the agent prepares a fresh draft. Local readiness alone does not
invalidate a historical packet or turn it into an approval.

`mcp-input.json` is emitted only if every selected file is UTF-8 text with a supported
extension (`txt`, `md`, `csv`, `json`, `tsv`, `xml`, `yaml`, `yml`), with at most ten
files, one million characters per file, a 100,000-character overview and two million
combined characters. Check discovered server limits again at handoff. No partial
payload is emitted when material is unsupported or oversized.

PDFs, spreadsheets, images, binaries and other unsupported files stay in the draft
with explicit blockers. On user direction, extract/convert using an appropriate
skill, retain the originals, label the extraction `derived`, link it to the source
item, and prepare a newly selected packet. Never claim a binary was uploaded through
a text-only attachment. Use another server upload capability only if discovered and
authorized; do not assume this helper performs uploads.

## Handoff to governed intake

Verify the packet immediately before using it. `mcp-input.json` contains material
for preparation (`title`, `submission.text`, `attachments`), not a completed tool
request or authorization to submit. Retrieve the receiving contract through MCP;
assign a new start idempotency key when creating the intake.
Use the current work's project context when invoking MCP and let the server
validate it. There is no project-discovery step: do not enumerate cases, scan
files or open a browser to establish a project. Local context is not authority.
For already selected items use prepare once, verify-packet once, then read its
mcp-input.json; do not run separate whole-bank verification or rebuild unchanged
exports. Let the prepare skill execute the handoff without another discovery pass.

Keep source statements and generated interpretations separate. Do not turn bank
categories/statuses into `fieldValues`, confirmed decisions, approved-source evidence
or human attestation. Resolve evidence relevance/access and contract requirements
through the existing server workflow, show the exact review, and preserve human
confirmation before sending. A local packet ID is not a server session or case ID.
