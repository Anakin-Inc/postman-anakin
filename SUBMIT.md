# Publishing Anakin on the Postman API Network

Route (from Postman's docs, checked 15 Oct 2026):
[prepare a public workspace](https://learning.postman.com/docs/postman-api-network/showcase/prepare/public-workspace/)
with an *API reference collection* and an *overview collection*, then
[change the workspace type to public](https://learning.postman.com/docs/postman-api-network/showcase/publish/public-apis/).
A public workspace and its collections appear on the API Network. Depending on plan and
role, a Community Manager on our own team may need to approve the switch. There is no
Postman-side review for listing; the optional
[verified publisher badge](https://learning.postman.com/docs/postman-api-network/showcase/prepare/verify-publisher-team/)
is a separate application (domain verification, then Postman reviews).

## What's built (this repo)

- `collections/anakin-api.postman_collection.json`: API reference, 70 requests / 13 folders.
- `collections/anakin-quickstart.postman_collection.json`: overview, first 200 OK with no key.
- `environments/anakin.postman_environment.json`: `baseUrl`, `apiKey` (secret, empty).

Verified 15 Oct 2026: both collections validate against the Collection v2.1 schema; the
keyless quickstart folder and Wire discovery run green against `api.anakin.io` with
newman; all 65 keyed routes reach Anakin's auth layer (401 with a dummy key). Keyed
requests have not been run with a real key yet (`ANAKIN_API_KEY=... npm test`).

## Steps (needs a Postman account owned by Anakin)

1. Sign in at https://www.postman.com with the company account (or create a team
   **Anakin**, team URL handle `anakin` if free, else `anakin-io`).
2. Team profile (https://www.postman.com/settings/team/general or *Team settings*):
   name **Anakin**, website `https://anakin.io`, logo from the brand kit, description:
   > Web data API: scrape any URL into Markdown or JSON, search, crawl and map sites, and run Wire actions on 940+ sites. Free tier, no card.
   Turn the public team profile on.
3. **Workspaces → Create workspace** → Blank → name **Anakin API**, type *Internal*
   (switch to Public in step 7). Summary:
   > Official Anakin collections: scrape, search, crawl, map, agentic search and Wire actions across 940+ sites.
4. In the workspace: **Import** → drop the 3 files above (from the repo, or these raw URLs
   once the branch is merged:
   `https://raw.githubusercontent.com/Anakin-Inc/postman-anakin/main/collections/anakin-api.postman_collection.json`,
   `.../collections/anakin-quickstart.postman_collection.json`,
   `.../environments/anakin.postman_environment.json`).
5. Select the **Anakin** environment. Run **Anakin Quickstart → 1. No key needed** (the
   three requests should return 200). Leave `apiKey` empty before publishing: Postman's
   secret scanner replaces keys anyway, but don't rely on it.
6. Workspace **Overview** tab: paste the Quickstart collection description, add link
   `https://anakin.io/docs/api-reference`.
7. Workspace settings → **Visibility / Workspace type → Public** → submit (approve the
   request if Postman asks a team admin to).
8. Send back: the public workspace URL and both collection URLs (Share → Copy link), and
   the **Run in Postman** button embed for the Quickstart collection (collection → Share →
   Via Run in Postman).
9. Optional, worth doing: **Public API Network → Settings → Postman verification**
   (https://www.postman.com/publisher/settings/verification), verify the `anakin.io`
   domain, **Submit for review**. Postman answers by email to the team admin.

## After it's public

- Add the Run in Postman button to the anakin.io docs (blueprint-scribe-35, integration
  install guides PR #1855, `webapp/content/docs/integrations/...`).
- Keep in sync: edit `scripts/build.py`, rebuild, re-import into the workspace (replace).
