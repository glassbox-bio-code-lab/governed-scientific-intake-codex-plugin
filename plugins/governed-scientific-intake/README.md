# Glassbox Bio Governed Promotion Intake plugin

This Codex plugin exposes four authenticated MCP actions through a configured
Glassbox service: `bank_work`, `prepare_promotion`, `review_promotion` and
`submit_promotion`. The local filesystem `intake-bank` skill can save work
without an upload. The prepare and submit skills are separate so an agent can
save a draft and later return to the same draft for human confirmation.

## Connection setup

Follow the [GitHub installation guide](../../README.md) from a stable clone.
Run `python3 scripts/configure.py list` or `show` here to inspect saved profiles.
`set NAME --mcp-url URL --api-url URL --web-url URL` saves a draft profile;
`use NAME` selects it, creates the nonsecret MCP configuration and installs the
plugin. `check NAME` probes endpoint reachability without a credential.
HTTPS is required away from explicit loopback addresses. Profile and account
credentials are stored under `~/.config/governed-scientific-intake/`, outside
this repository. The package's initial helper path is deliberately unconfigured;
run `use NAME` before using MCP tools.

`python3 scripts/login.py` checks the selected API before asking for an account
username and password in the terminal. The password is hidden. The resulting
credential is stored with owner-only permissions and bound to the exact profile
and endpoint addresses. The HTTP MCP transport invokes `scripts/auth_headers.py`
from the stable checkout to read that credential for each connection. It never
passes credentials in model-visible tool arguments. The local session expires
after eight hours; log in again and reconnect then. Keep the checkout in place
while the plugin is installed.

After `use` or login, reconnect the plugin or restart Codex and start a new
task. Existing tasks may retain an earlier connection or tool list. A 401 from
an unauthenticated MCP reachability probe shows that the endpoint is responding;
it does not prove a working account connection. If tools are absent, check the
selected endpoints, run login, reconnect and start a new task.

## Promotion flow

`bank_work` saves explicitly selected work to the authenticated account and
project without promoting it. The local `intake-bank` skill saves a separate
filesystem copy when requested. `prepare_promotion` accepts actual selected
conversation text, receiver and project, or selected server bank item IDs;
Glassbox returns a durable draft summary, questions and review link.
`review_promotion` reads or corrects that same draft. `submit_promotion` starts
from its saved draft ID and uses the server's human confirmation route or its
authenticated web review. A saved draft or review link is not a submission
receipt; report only the returned outcome. Decline and cancel stop the attempt.
The service, not the plugin, controls authorization, requirements, provenance,
evidence status and submission.

A service operator supplies the API, MCP and web endpoints. The MCP transport is
separate from FastAPI and must share its configured backend. The plugin only
connects to those services; it does not deploy them.
