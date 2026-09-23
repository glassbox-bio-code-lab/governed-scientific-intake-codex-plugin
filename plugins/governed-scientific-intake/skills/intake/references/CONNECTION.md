# Connection to the Glassbox service

Read [ACTIVE_CONNECTION.md](ACTIVE_CONNECTION.md) for the selected profile, MCP
endpoint, API base and web review base. The GitHub checkout must remain at the
stable location used during installation because its helper supplies the MCP
credential from the user's private configuration. The helper never takes a token
from chat or tool arguments.

From the plugin directory in that checkout, run `python3 scripts/configure.py
list`, `show`, or `check NAME`. To save a different operator-provided endpoint
set, use `set NAME --mcp-url URL --api-url URL --web-url URL`, followed by `use
NAME`; then sign in privately with `python3 scripts/login.py`. The service
operator provides account access. Reconnect the plugin and start a new task
after a profile switch or renewed login. Do not reuse a draft ID across
unrelated deployments.

The HTTP MCP service is separate from the API and web review app. HTTP 401 on
an unauthenticated reachability probe only means the endpoint answered. If
MCP tools are absent, first check the profile, private login and new-task
connection. Do not ask for credentials in chat, register a duplicate MCP
server or use a pilot token for an account.
