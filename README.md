# Glassbox Bio Governed Promotion Intake for Codex

This public repository contains the Codex plugin and its portable instructions. It
connects to a separately operated Glassbox API, MCP service and web application.
The backend, receiving contracts, accounts and scientific data are not included.

## Install from GitHub

Keep the GitHub checkout in a stable location. Connection setup binds its private
credential helper to that checkout, so do not delete it while the plugin is installed.
Python 3 and the Codex CLI must be available on the local computer.

```bash
git clone https://github.com/glassbox-bio-code-lab/governed-scientific-intake-codex-plugin.git "$HOME/.local/share/glassbox-bio-governed-intake"
cd "$HOME/.local/share/glassbox-bio-governed-intake"
codex plugin marketplace add "$PWD"
python3 plugins/governed-scientific-intake/scripts/configure.py use local
```

`use local` installs `governed-scientific-intake@glassbox-bio-intake` and binds its
MCP connection to the checkout. The default local endpoints are MCP
`http://127.0.0.1:8140/mcp`, API `http://127.0.0.1:8010`, and web review
`http://127.0.0.1:5173`. These services must already be running and use the
same backend. A credential-free `configure.py check local` checks reachability.

For another deployment, save the operator-provided HTTPS endpoints before use:

```bash
python3 plugins/governed-scientific-intake/scripts/configure.py set production \
  --mcp-url https://intake.example.org/mcp \
  --api-url https://intake.example.org \
  --web-url https://intake.example.org
python3 plugins/governed-scientific-intake/scripts/configure.py use production
```

The account owner signs in through a private terminal prompt:

```bash
python3 plugins/governed-scientific-intake/scripts/login.py
```

Reconnect the plugin or restart Codex, then start a new task. Never put a
password or token in chat, command arguments or the repository. Setup does not
create, approve or submit a promotion packet. The Codex desktop app and CLI use
the same installed plugin and saved connection; no special app launcher is needed.
See the [plugin guide](plugins/governed-scientific-intake/README.md) for profile
management, token expiry, the four MCP actions and local banking.

## Update or remove

Run `git pull` in the checkout and `python3 plugins/governed-scientific-intake/scripts/configure.py use <saved-profile>`
to install the updated package. Use `codex plugin remove governed-scientific-intake@glassbox-bio-intake`
to uninstall. A saved private login and the Git checkout are separate from the
Codex installation; remove them only when you intend to discard them.

## License

Code and documentation are available under the [MIT License](LICENSE). The
Glassbox Bio name and logo are brand assets excluded from that grant. Their
inclusion does not grant trademark or endorsement rights. No backend, user data,
or deployment credentials are licensed or distributed here.
