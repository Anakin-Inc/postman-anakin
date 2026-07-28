# Postman API Network — submission instructions

## What's ready

`wire-webapp/public/openapi.yaml` is a complete, real OpenAPI 3.1 spec for
the **Wire API** (`api.openwire.sh/v1/wire` — discover/run pre-built actions
across hundreds of sites, plus identities/login). It's the actual source of
truth already used to build the Wire docs, not something drafted for this
submission — importing it into Postman is close to the entire task.

## What's NOT ready — scope gap worth fixing before or alongside this

**Only Wire has a machine-readable spec.** The core product surface —
`url-scraper`, `search`, `crawl`, `map`, `monitoring`, `browser-connect`,
`browser-sessions`, `agentic-search`, `ai-visibility` — is documented as
hand-written `.mdx` pages under `webapp/content/docs/api-reference/`, not an
OpenAPI file. A Postman collection built only from the Wire spec covers one
product surface, not "Anakin's API" as a whole — worth flagging to whoever
owns the Postman listing before publishing it as *the* Anakin collection,
since it'll read as complete when it's partial.

Two ways to close that gap, not attempted here (out of scope for a
same-day submission task, and risks drifting from the real API if hand-
authored from docs rather than generated from the Go handlers):
1. Generate one from `api/`'s Fiber handlers (e.g. `swaggo/swag` annotations
   → `swag init`) — stays in sync with the real routes automatically.
2. Hand-author a second OpenAPI file mirroring the `.mdx` docs — faster
   short-term, drifts the moment an endpoint changes and nobody updates it.

## Steps to publish what's ready (needs the account owner)

1. Confirm `openapi.yaml` is actually served at a stable public URL (checked
   2026-07-27: `openwire.sh/openapi.yaml` and `api.openwire.sh/openapi.yaml`
   both 404 — the file exists in `wire-webapp/public/` but isn't confirmed
   deployed at either path; verify the actual deployed URL, or import the
   local file directly as a one-time upload instead of a URL reference).
2. In Postman: **Import** → OpenAPI 3.1 → point at the confirmed URL (or
   upload the file directly if no stable URL exists yet).
3. Postman generates a collection from the spec automatically — review the
   generated request names/folders match the spec's `tags` (Discovery,
   Tasks, Identities) before publishing.
4. **Publish to API Network**: workspace → the imported API → Publish →
   fill in the network listing (name, description, docs link to
   `anakin.io/docs`).
5. Set up a **workspace** (`Anakin` team workspace) if one doesn't exist yet,
   so the published API has a home other than a personal workspace.

## Not done

Requires a Postman account under the account owner and confirming the
spec's live URL — nobody has run the import/publish flow yet.
