# Glassbox Bio Governed Promotion Intake for Codex

This public repository contains one Codex plugin. It connects Codex app or CLI
to an existing Governed Scientific Intake MCP server and includes a local
`intake-bank` skill for saving selected material before promotion.
`intake-prepare` and `intake-submit` are separate callable skills so preparation
stops at a saved draft and sending starts from a reviewed existing session. The backend,
accounts, and scientific data are not part of this repository.
Its tool reference and agent instructions intentionally describe the public
integration workflow. Keep receiver-specific contracts, real evidence, packet
exports, account configuration and credentials out of this repository.

## Install from a local clone

```bash
git clone https://github.com/glassbox-bio-code-lab/governed-scientific-intake-codex-plugin.git
cd governed-scientific-intake-codex-plugin
codex plugin marketplace add "$PWD"
codex plugin add governed-scientific-intake@glassbox-bio-intake
```

The plugin starts with loopback addresses: MCP at
`http://127.0.0.1:8140/mcp`, API at `http://127.0.0.1:8010`, and web review at
`http://127.0.0.1:5173`. The MCP service is a **separate process** from the
FastAPI service. Both must point to the same configured backend. The plugin
only connects to these services; it does not start or deploy them.

For a different deployment, use the source in this clone:

```bash
cd plugins/governed-scientific-intake
python3 scripts/configure.py set lab \
  --mcp-url https://intake.example.org/mcp \
  --api-url https://intake.example.org \
  --web-url https://intake.example.org
python3 scripts/configure.py check lab
python3 scripts/configure.py use lab
python3 scripts/login.py
```

`use` updates the selected addresses in the local plugin and reinstalls it
from this marketplace. `login.py` prompts in the terminal and stores the
session credential privately under your home directory. Then fully quit
Codex and relaunch it through `plugins/governed-scientific-intake/scripts/with-token.sh`:

```bash
cd ../..
plugins/governed-scientific-intake/scripts/with-token.sh codex
```

For the desktop app, pass its executable instead of `codex`. Start a new task
after relaunching. The exact API and MCP URLs must match a running deployment,
and the account must be authorized for that receiver and project.

See [the plugin guide](plugins/governed-scientific-intake/README.md) for
connection profiles, review, confirmation and token lifetime. The companion
[portable agent skills](https://github.com/glassbox-bio-code-lab/governed-scientific-intake-agent-skills)
can be installed into other agents independently.

This package preserves the service's human review boundary: an agent prepares
material and may request an actual human-facing confirmation form or browser
review; it never supplies its own approval.

## License

The code and documentation in this repository are available under the [MIT License](LICENSE).
The Glassbox Bio name and logo are excluded from the MIT grant and remain brand
assets of Glassbox Bio; their inclusion does not grant trademark or endorsement rights.
The separate backend service, user data, and deployment credentials are not
included in this repository or licensed by this file.
