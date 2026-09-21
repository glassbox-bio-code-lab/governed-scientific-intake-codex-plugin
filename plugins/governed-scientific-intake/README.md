# Glassbox Bio Governed Promotion Intake Codex plugin

Prepare governed scientific handoffs using native authenticated HTTP MCP. Named
connection profiles configure the MCP server, login API and web review application
as a unit. The shipped `local` profile uses ports 8140, 8010 and 5173 respectively.

## Connection setup

Run these commands from the registered local plugin source. In the standalone
GitHub marketplace clone, that is `plugins/governed-scientific-intake`; in a
personal marketplace, it is `~/plugins/governed-scientific-intake`:

```bash
python3 scripts/configure.py list
python3 scripts/configure.py show
python3 scripts/configure.py check local
python3 scripts/configure.py use local
```

`check` performs credential-free reachability probes. It does not establish server
identity, authenticated access or workflow compatibility. `use` regenerates the
selected connection files, refreshes the package version and reinstalls through
`codex plugin add`. It checks the installed snapshot before changing active state.
A failed/ambiguous installation leaves the previous active profile intact; rerun
`use` to repair it. Run setup against the registered local source, not by editing
the cache. Codex must be installed and available on PATH. This helper supports
the personal and standalone local Git marketplaces on Linux/macOS.

To add or edit another deployment (replace these example addresses):

```bash
python3 scripts/configure.py set staging \
  --mcp-url https://intake.example.org/mcp \
  --api-url https://intake.example.org \
  --web-url https://intake.example.org
python3 scripts/configure.py check staging
python3 scripts/configure.py use staging
```

`set` saves a draft profile; it does not switch an active connection, even when
editing the active profile's name. `use` explicitly activates its saved values.
`show NAME` displays a saved profile; `show` displays the active snapshot. Paths
behind a reverse proxy are supported: the API base gets `/api/v1/auth/login`
appended; the web base gets relative review/receipt paths appended. The MCP URL
must be the full endpoint. HTTPS is required except for explicit loopback addresses.
URLs cannot contain credentials, query strings, fragments or encoded path segments.

Profiles live in `~/.config/governed-scientific-intake/connections.json`, outside
plugin updates. The package contains only the selected nonsecret `connection.json`,
MCP configuration and selected connection notes in the prepare, submit and legacy skills. Reapplying
`use NAME` after a plugin update restores that saved profile to the new package.
There is no custom native Codex settings panel.

## Login and launch

After activating a connection, the user runs:

```bash
python3 scripts/login.py
```

The helper displays the selected API/MCP addresses, asks for the Governed Intake
account username/password in the terminal, and logs into that API. It verifies TLS
for HTTPS and disables redirects and ambient HTTP proxies. It stores an owner-only
credential under `~/.config/governed-scientific-intake/credentials/`, bound to the
profile name and all three exact normalized URLs. It never prints the credential.
A new profile or any changed address requires a separate login. The old unbound
`mcp-token` file is intentionally not reused or deleted; login again after upgrading.

Fully quit the existing desktop process, then launch it with:

```bash
scripts/with-token.sh /usr/bin/chatgpt
```

For the CLI:

```bash
scripts/with-token.sh codex
```

Start a new task. The launcher checks that the package matches the active profile,
loads its private credential and exports only its endpoint-specific
`GSI_MCP_TOKEN_<connection hash>` variable. Old inherited intake-token variables are
removed. An already-running desktop has the old environment; merely opening a new
task cannot change it. Existing tasks remain attached to their old server/context;
do not carry their session or case IDs to another deployment.

The local account token expires after eight hours. Login and relaunch when it
expires. Do not place passwords/tokens or `user_id` in agent tool arguments, chat,
attachments, URLs or plugin source. No account login or submission occurs during
`set`, `use` or `check`.

## Local server and approval

The service operator must provide running API, MCP and web-review addresses. The
MCP process is separate from the API and must use the same backend configuration.
Connection setup configures the client; it does not deploy servers.

`$intake-prepare` prepares a durable session and stops at a saved draft.
`$intake-submit` starts from that session, shows the current review and proceeds
through human confirmation or authenticated browser review. `$intake-bank` saves
selected material locally for later preparation.
The optional `request_intake_confirmation` tool requires actual human-facing MCP
forms; the agent cannot answer them. Otherwise use authenticated browser review.
A decline/cancel stops the attempt. `needs_evidence` is saved, not sent. A signed
receipt is not proof of scientific correctness or completed verification.

## Shared skill and Codex adapter

The separately published `governed-intake-prepare` and `governed-intake-submit`
skills provide portable phase-specific entrypoints. The older
`governed-intake-agent` remains for compatibility. Each platform has separate
entrypoints, metadata and connection instructions.

## Save work before promotion

Call `$intake-bank` to save specified notes, documents, evidence or results for later.
It needs no login or MCP connection. By default it uses a stable project's
`.intake-bank/` with a JSON index, copied file snapshots, provenance and selected
draft packets. It reports absolute paths and item IDs for later tasks.

Example prompts:

- “Use $intake-bank to save these results for a future promotion packet.”
- “Show the items I saved for the formulation study.”
- “Prepare a draft packet from these three saved items; do not submit it.”

The portable helper is `skills/intake-bank/scripts/bank.py`; its commands are
`init`, `add`, `list`, `show`, `update`, `verify`, `prepare`, and `verify-packet`.
Read [the bank workflow](skills/intake-bank/references/workflow.md) and
[directory format](skills/intake-bank/references/layout.md) for usage.

Stored evidence remains unverified local material. Binary documents are preserved
and flagged when the text-only MCP interface cannot accept them. Packet preparation
uses explicit selection and performs no upload or submission. The separate portable
skill repository includes both the governed intake and bank skills.
