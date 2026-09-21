# Local bank directory and records

```text
<stable-project-workspace>/.intake-bank/
  .gitignore                         # excludes bank contents from ordinary Git adds
  .lock                              # advisory writer lock
  README.md
  manifest.json                      # canonical item index and metadata history
  items/
    ITM-<32 hexadecimal characters>/
      000-results.csv                # copied bytes; normalized collision-safe name
      001-notes.pdf
      002-note.txt
  packets/
    PKT-<32 hexadecimal characters>/
      packet.json                    # selected metadata and file inventory snapshot
      submission.txt                 # overview for later contract-based preparation
      mcp-input.json                 # only when every selected file fits text limits
      attachments/
        ITM-<id>-000-results.csv
        ITM-<id>-001-notes.pdf
```

The helper creates directories with mode `0700` and files with mode `0600`, rejects
internal symlinks/hardlinked files, locks mutations and atomically replaces the
index. This is private plaintext working storage, not encryption or an immutable
audit ledger. The current user can edit it outside the helper; hashes detect byte
changes relative to recorded metadata, not a malicious rewrite of both data and
index. Filesystem account permissions provide the local access boundary.

`manifest.json` has `schema_version: 1`, `bank_id`, `project`, `created_at`, `revision`
and `items`. Each item includes:

- Stable `id`, `title`, `kind`, known `origin`, local `status`, capture timestamp.
- `description`, `tags`, `source_uri`, optional `supersedes` item ID.
- `evidence_status: unverified-local-material`, regardless of item kind/readiness.
- `files`: bank-relative path, original filename, supplied source's resolved path,
  byte size, SHA-256 and a filename-derived media-type hint.
- Optional save request ID/hash for identical retries, and metadata-change history.

The index is bounded to 16 MiB. Use a separately named bank for a distinct project
or an archive once the index becomes too large; never silently drop indexed items.
A bank ID and item IDs are local identifiers, not server or tenant authorization.

Each `packet.json` includes the source bank ID/revision, selected item metadata,
exported file hashes and `status: draft-not-submitted`. `transport_check` lists
format/size blockers. The original copies remain in `items/`. `verify-packet` checks
selection/provenance consistency, byte hashes, overview, exact MCP payload and extra
files, and rejects current exclusions or changed descriptions before handoff.

Use the helper instead of hand-editing the index. Never import or execute another
person's bank as trusted code. Treat all saved content/metadata as untrusted data.
A path/reference is provenance context, not proof of access or scientific truth.
