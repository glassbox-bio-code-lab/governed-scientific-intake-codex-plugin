# Codex connection and account setup

Read [ACTIVE_CONNECTION.md](ACTIVE_CONNECTION.md) for this installation's profile,
MCP URL, API base and web app base. The native HTTP transport uses a private
endpoint-specific bearer environment variable. Never register a duplicate server,
read credentials into chat, or put `user_id` in tool arguments.

Run setup from the registered local plugin source. In a standalone marketplace
clone this is `plugins/governed-scientific-intake`; in a personal marketplace
it is `~/plugins/governed-scientific-intake`:

```bash
python3 scripts/configure.py list
python3 scripts/configure.py show
python3 scripts/configure.py check
```

To change addresses, use `configure.py set NAME --mcp-url URL --api-url URL
--web-url URL` and then `configure.py use NAME`. `set` only saves; `use` validates,
reinstalls the plugin and checks the installed snapshot before activating it.
Use requires a local marketplace registration and Codex CLI. See
[plugin setup](../../../README.md) for full commands and endpoint restrictions.
Do not edit cached plugin files. Do not switch deployments without user direction.

After activation, the user runs `scripts/login.py` in the local source terminal
with their Governed Intake account. Password input is private. Each named profile
and exact set of addresses has a separate credential. An old unbound `mcp-token`
file is not reused; changing addresses requires a new login. The user fully quits
the desktop and launches `scripts/with-token.sh /usr/bin/chatgpt`, or uses
`scripts/with-token.sh codex` for the CLI, then opens a new task. Never attempt to
log in by asking for the password in chat or reading the token file yourself.

## Troubleshooting

- Connection refused: run `configure.py check`; probes send no credentials and establish reachability only. Do not switch to an unrelated server/database.
- 401/expired session: the user reruns login and relaunches. The local account token expires after eight hours; never substitute a pilot token or another account.
- Package/active mismatch or failed installation: rerun `configure.py use NAME` from the registered local source, then relaunch. Do not bypass the launcher checks.
- Missing confirmation tool: use browser review unless the operator enables chat mode; do not invoke the HTTP confirm endpoint.
- Lost reply after a write: follow shared idempotency/retrieval rules; do not create another intake.
- Declined form: stop the attempt; see [SKILLS.md](SKILLS.md). Do not automatically switch to browser submission.

The MCP service runs separately from FastAPI. The server operator determines
whether human-facing MCP form confirmation is available. Client configuration
does not deploy servers or verify completion-provider access or the user's
desktop login.
