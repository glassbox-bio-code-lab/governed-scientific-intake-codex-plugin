# Codex integration notes

The default authenticated MCP surface has four business actions: `bank_work`,
`prepare_promotion`, `review_promotion` and `submit_promotion`. Discover the
actual schemas from the connected server. Use the selected web app base in
[ACTIVE_CONNECTION.md](ACTIVE_CONNECTION.md) to resolve relative review URLs.
The server cannot see local files or the current conversation unless selected
content is supplied through the appropriate action.

Preparation returns a saved draft and questions, not a sent packet. Submit only
when the user asks and use the existing draft ID. A real user-facing form or
authenticated web review makes the human decision; the agent never supplies
its own acceptance. `needs_evidence` and `needs_human_review` are not receipts.
Return the server's actual receipt if a submission succeeds.

The installed HTTP connection obtains credentials from a private helper.
Keep credentials, passwords and account identity out of model-visible tool
arguments. Report a missing login or connection plainly and let the account
owner use the private terminal login command in the plugin guide.
