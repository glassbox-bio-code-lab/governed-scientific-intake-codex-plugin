---
name: intake
description: Bank work, prepare or review a Glassbox promotion draft, or submit it with human confirmation through four MCP actions.
---

# Glassbox promotion

Use the configured Glassbox MCP connection:

- `bank_work`: save selected material in Glassbox for later promotion.
- `prepare_promotion`: prepare a draft for the receiver and project in one call.
- `review_promotion`: read the review summary or apply follow-up answers.
- `submit_promotion`: request human confirmation and send when the user asks.

Pass actual selected text; Glassbox cannot read the client conversation or local
files implicitly. Use existing project context and retain the returned draft ID.
Show the returned summary, questions and review URL. Resolve relative paths
against the web app base in [the selected connection](references/ACTIVE_CONNECTION.md). Detailed provenance,
confirmation and receiver review live in Glassbox. Reuse idempotency keys on
uncertain retries. Never supply credentials in model-visible arguments or answer
human confirmation yourself. Do not use reviewer or contract-governance mutations
for a sender promotion.

For explicitly local/offline banking, use the companion intake-bank filesystem
workflow. Local material is uploaded only when the user asks to promote it.
Legacy tools are available through an explicit advanced server profile;
[the advanced tool contract](references/tool_contract.md) documents that profile.
