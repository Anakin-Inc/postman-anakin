#!/usr/bin/env python3
"""Generate the Anakin Postman collections and environment.

Source of truth for endpoints: https://anakin.io/docs/api-reference
(https://anakin.io/llms-full.txt). Edit the tables below, then run:

    python3 scripts/build.py

Outputs:
    collections/anakin-api.postman_collection.json         API reference (every endpoint)
    collections/anakin-quickstart.postman_collection.json  Overview: first 200 OK, no key needed
    environments/anakin.postman_environment.json           baseUrl + apiKey placeholders
"""
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = "https://anakin.io/docs/api-reference"
SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"

# Deterministic ids so regenerating does not churn the diff.
def uid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "anakin-postman/" + "/".join(parts)))


def capture(var, *fields):
    """Test script: store the first present field of the JSON response in a collection variable."""
    lookups = " ?? ".join("body?." + f.replace(".", "?.") for f in fields)
    return [
        "let body = {};",
        "try { body = pm.response.json(); } catch (e) {}",
        f"const value = {lookups};",
        f"if (value) {{ pm.collectionVariables.set('{var}', value); }}",
    ]


def status_ok():
    return [
        "pm.test('Status is 2xx', () => pm.expect(pm.response.code).to.be.within(200, 299));",
    ]


def req(name, method, path, desc, docs, body=None, query=None, keyless=False, tests=None):
    return {
        "name": name, "method": method, "path": path, "desc": desc, "docs": docs,
        "body": body, "query": query or [], "keyless": keyless, "tests": tests or [],
    }


# ---------------------------------------------------------------------------
# API reference collection
# ---------------------------------------------------------------------------
REFERENCE = [
    ("URL Scraper", "Scrape a page into Markdown, cleaned HTML, or structured JSON. Handles proxies, JavaScript rendering, and anti-bot protection.", [
        req("Scrape URL (inline)", "POST", "/url-scraper/scrape",
            "Scrape one URL and get the result in the same response, no polling. Works without an API key on the free Zero Touch trial; add `X-API-Key` for full limits.",
            "url-scraper/scrape",
            {"url": "https://example.com", "country": "us", "useBrowser": False, "generateJson": False}),
        req("Submit scrape job", "POST", "/url-scraper",
            "Submit an asynchronous scrape job. Returns a `jobId`; poll **Get scrape result**. The job id is saved to the `scrapeJobId` collection variable.",
            "url-scraper/submit-scrape-job",
            {"url": "https://example.com", "country": "us", "useBrowser": False, "generateJson": False},
            tests=capture("scrapeJobId", "jobId")),
        req("Submit batch scrape job", "POST", "/url-scraper/batch",
            "Scrape up to many URLs in one job. Poll **Get scrape result** with the returned `jobId`.",
            "url-scraper/batch-url-scraping",
            {"urls": ["https://example.com/page1", "https://example.com/page2"], "country": "us", "useBrowser": False, "generateJson": True},
            tests=capture("scrapeJobId", "jobId")),
        req("Get scrape result", "GET", "/url-scraper/{{scrapeJobId}}",
            "Poll a scrape or batch job. `status` moves from `pending`/`processing` to `completed` or `failed`.",
            "url-scraper/get-job-status"),
        req("Download screenshot", "GET", "/url-scraper/{{scrapeJobId}}/screenshot",
            "Download the screenshot captured for a scrape job. Use `type=fullpage` for a full-page capture.",
            "url-scraper/get-screenshot", query=[("type", "fullpage", True)]),
    ]),
    ("Search", "Web search that returns results with extracted page content.", [
        req("Search", "POST", "/search",
            "Run a web search and get results with content, synchronously.",
            "search/search", {"prompt": "latest AI developments", "limit": 5}),
    ]),
    ("Agentic Search", "Multi-stage AI research pipeline: search, read, and synthesize an answer with sources.", [
        req("Submit research query", "POST", "/agentic-search",
            "Start an agentic research job. The `job_id` is saved to `agenticSearchId`.",
            "agentic-search/submit-search",
            {"prompt": "Comprehensive analysis of quantum computing trends"},
            tests=capture("agenticSearchId", "job_id", "jobId", "id")),
        req("Get research result", "GET", "/agentic-search/{{agenticSearchId}}",
            "Poll the research job until `status` is `completed`.",
            "agentic-search/get-search-result"),
    ]),
    ("Map", "Discover every URL on a website.", [
        req("Submit map job", "POST", "/map",
            "Start a URL discovery job. The `jobId` is saved to `mapJobId`.",
            "map/submit-map-job",
            {"url": "https://example.com", "includeSubdomains": False, "limit": 100},
            tests=capture("mapJobId", "jobId")),
        req("Get map result", "GET", "/map/{{mapJobId}}",
            "Poll the map job for the discovered URLs.", "map/get-map-result"),
    ]),
    ("Crawl", "Crawl a website and extract content from each page.", [
        req("Submit crawl job", "POST", "/crawl",
            "Start a crawl. The `jobId` is saved to `crawlJobId`.",
            "crawl/submit-crawl-job",
            {"url": "https://example.com", "maxPages": 20, "includePatterns": ["/blog/*"], "country": "us"},
            tests=capture("crawlJobId", "jobId")),
        req("Get crawl result", "GET", "/crawl/{{crawlJobId}}",
            "Poll the crawl job for page results.", "crawl/get-crawl-result"),
    ]),
    ("Wire / Discovery", "Wire turns 940+ sites into API actions. Discovery is public: no API key needed.", [
        req("Resolve actions by intent", "GET", "/wire/resolve",
            "Find Wire actions for a plain-language intent. Returns `action_id`s and their params. No API key needed.",
            "wire/search-actions", query=[("q", "hacker news top stories", False)], keyless=True),
        req("List catalogs", "GET", "/wire/catalog",
            "List every site Wire supports. No API key needed.", "wire/list-catalogs", keyless=True),
        req("Get catalog details", "GET", "/wire/catalog/{{catalogSlug}}",
            "Actions, parameters, credit cost, and auth requirement for one site. No API key needed.",
            "wire/get-catalog", keyless=True),
    ]),
    ("Wire / Run", "Run Wire actions. `wire-run` is the synchronous, keyless, read-only mode; `wire/task` is the keyed, asynchronous mode for write actions and account-connected runs.", [
        req("Run read-only action (no key)", "POST", "/wire-run",
            "Run a read-only Wire action synchronously with no API key. The result comes back inline.",
            "wire", {"action_id": "hn_stories", "params": {"limit": 5}}, keyless=True),
        req("Execute task", "POST", "/wire/task",
            "Run any Wire action asynchronously. Auth-gated actions need a `credential_id` (see **Wire / Identities**). The `job_id` is saved to `wireJobId`.",
            "wire/execute-task",
            {"action_id": "hn_stories", "params": {"limit": 5}},
            tests=capture("wireJobId", "job_id", "jobId")),
        req("Get job status", "GET", "/wire/jobs/{{wireJobId}}",
            "Poll a Wire job (about once a second, capped at 60/min per user).", "wire/get-job"),
        req("Download job file", "GET", "/wire/jobs/{{wireJobId}}/download",
            "Download the file produced by a Wire job, when the action returns one.", "wire/get-job-download"),
        req("Request a new action", "POST", "/wire/build-request",
            "Ask Anakin to build a Wire action for a site that is not in the catalog yet.",
            "wire/create-build-request",
            {"website_url": "https://example.com", "goal": "Extract product name, price, and availability from a product page"}),
    ]),
    ("Wire / Identities", "Identities let Wire run actions on sites that need a login. Credentials are never stored as plaintext.", [
        req("Create identity (login)", "POST", "/wire/login",
            "Log in to a site to create an identity whose `credential_id` you pass to **Execute task**.",
            "wire/login",
            {"catalog_slug": "{{catalogSlug}}", "params": {"email": "you@example.com", "password": "your_password"}}),
        req("List identities", "GET", "/wire/identities", "List your identities.", "wire/list-identities"),
        req("Get identity", "GET", "/wire/identities/{{identityId}}", "Get one identity.", "wire/list-identities"),
        req("Verify identity (re-login)", "POST", "/wire/credentials/verify",
            "Check an identity still works, re-authenticating if needed.",
            "wire/verify-credential", {"identity_id": "{{identityId}}"}),
    ]),
    ("Wire / Identity Sources", "Connect a password manager (for example 1Password) so Wire can log in with credentials you already store there.", [
        req("List providers", "GET", "/wire/identity-sources/providers", "Supported identity source providers.", "wire/list-providers"),
        req("Connect source", "POST", "/wire/identity-sources",
            "Connect a provider. The source `id` is saved to `identitySourceId`.",
            "wire/create-identity-source",
            {"provider": "1password", "display_name": "Engineering vault", "token": "{{providerToken}}"},
            tests=capture("identitySourceId", "id")),
        req("List sources", "GET", "/wire/identity-sources", "List connected sources.", "wire/list-identity-sources"),
        req("Get source", "GET", "/wire/identity-sources/{{identitySourceId}}", "Get one source.", "wire/get-identity-source"),
        req("Rename or rotate source", "PATCH", "/wire/identity-sources/{{identitySourceId}}",
            "Rename a source or rotate its token.", "wire/update-identity-source",
            {"display_name": "Engineering vault (prod)"}),
        req("Verify source", "POST", "/wire/identity-sources/{{identitySourceId}}/verify",
            "Check the source's token still works.", "wire/verify-identity-source"),
        req("List containers", "GET", "/wire/identity-sources/{{identitySourceId}}/containers",
            "List vaults or folders in a source.", "wire/list-source-containers"),
        req("List entries", "GET", "/wire/identity-sources/{{identitySourceId}}/containers/{{containerId}}/entries",
            "List entries in a container.", "wire/list-source-entries"),
        req("Identities using a source", "GET", "/wire/identity-sources/{{identitySourceId}}/identities",
            "List identities built from this source.", "wire/list-source-identities"),
        req("Disconnect source", "DELETE", "/wire/identity-sources/{{identitySourceId}}",
            "Disconnect a source.", "wire/delete-identity-source"),
    ]),
    ("Monitoring", "Watch a page or a whole site and get alerted when it changes.", [
        req("Create monitor", "POST", "/monitors",
            "Create a monitor. The `id` is saved to `monitorId`.",
            "monitoring/create-monitor",
            {"url": "https://example.com/product/123", "watchMode": "specific_data",
             "outputSchema": {"type": "object", "properties": {"price": {"type": "number"}}, "required": ["price"]},
             "intervalMinutes": 60, "alertWebhookUrl": "https://your-app.com/hooks/anakin"},
            tests=capture("monitorId", "id", "monitor.id")),
        req("List monitors", "GET", "/monitors", "List your monitors.", "monitoring/list-monitors"),
        req("Get monitor", "GET", "/monitors/{{monitorId}}", "Get one monitor.", "monitoring/list-monitors"),
        req("Update monitor", "PUT", "/monitors/{{monitorId}}", "Replace a monitor's configuration.",
            "monitoring/update-monitor",
            {"url": "https://example.com/product/123", "watchMode": "full_page", "intervalMinutes": 240}),
        req("Run now", "POST", "/monitors/{{monitorId}}/run", "Trigger a check immediately.", "monitoring/control-monitor"),
        req("Pause", "POST", "/monitors/{{monitorId}}/pause", "Pause a monitor.", "monitoring/control-monitor"),
        req("Resume", "POST", "/monitors/{{monitorId}}/resume",
            "Resume a monitor. Optionally send `{\"expiresAt\": \"YYYY-MM-DD\"}` to set an end date.",
            "monitoring/control-monitor"),
        req("Set end date", "POST", "/monitors/{{monitorId}}/expiry",
            "Change only the end date. Send `null` to run indefinitely.", "monitoring/control-monitor",
            {"expiresAt": "2026-12-31"}),
        req("List changes", "GET", "/monitors/{{monitorId}}/changes", "Detected changes.", "monitoring/snapshots-and-changes"),
        req("List snapshots", "GET", "/monitors/{{monitorId}}/snapshots", "Stored snapshots.", "monitoring/snapshots-and-changes"),
        req("Get snapshot content", "GET", "/monitors/{{monitorId}}/snapshots/{{snapshotId}}/content",
            "Content of one snapshot.", "monitoring/snapshots-and-changes"),
        req("List site runs", "GET", "/monitors/{{monitorId}}/runs", "Runs of a site monitor.", "monitoring/site-monitors"),
        req("List site pages", "GET", "/monitors/{{monitorId}}/pages", "Pages tracked by a site monitor.", "monitoring/site-monitors"),
        req("Send test alert", "POST", "/monitors/{{monitorId}}/test-alert", "Send a test alert to the monitor's destinations.", "monitoring/alerts"),
        req("List alert deliveries", "GET", "/monitors/{{monitorId}}/deliveries", "Alert delivery attempts.", "monitoring/alerts"),
        req("Retry alert delivery", "POST", "/monitors/{{monitorId}}/deliveries/{{deliveryId}}/retry", "Retry one alert delivery.", "monitoring/alerts"),
        req("Delete monitor", "DELETE", "/monitors/{{monitorId}}", "Delete a monitor.", "monitoring/update-monitor"),
    ]),
    ("AI Visibility", "See what ChatGPT, Gemini, Perplexity and other AI engines answer for a query.", [
        req("List sources", "GET", "/ai-visibility/sources", "Supported AI engines.", "ai-visibility/list-sources"),
        req("Submit search", "POST", "/ai-visibility/search",
            "Ask several AI engines the same query. The `search_id` is saved to `aiVisibilitySearchId`.",
            "ai-visibility/submit-search",
            {"query": "Best coding agents in 2026", "sources": ["chatgpt", "gemini"]},
            tests=capture("aiVisibilitySearchId", "search_id", "id")),
        req("Get search", "GET", "/ai-visibility/search/{{aiVisibilitySearchId}}", "Poll results per source.", "ai-visibility/get-search"),
        req("List searches", "GET", "/ai-visibility/searches", "Your past searches.", "ai-visibility/list-searches"),
        req("Retry source", "POST", "/ai-visibility/search/{{aiVisibilitySearchId}}/retry",
            "Retry one engine that failed.", "ai-visibility/retry-source", {"source": "gemini"}),
    ]),
    ("Browser Sessions", "Saved browser sessions for scraping pages behind a login.", [
        req("List sessions", "GET", "/sessions", "List saved sessions.", "browser-sessions"),
        req("Rename session", "PATCH", "/sessions/{{sessionId}}", "Rename a saved session.", "browser-sessions",
            {"name": "new-session-name"}),
        req("Delete session", "DELETE", "/sessions/{{sessionId}}", "Delete a saved session.", "browser-sessions"),
    ]),
    ("Webhooks", "Get job and monitor events pushed to your endpoint instead of polling.", [
        req("List event types", "GET", "/webhooks/events", "Event types you can subscribe to.", "webhooks/events"),
        req("Create endpoint", "POST", "/webhooks",
            "Register an endpoint. The `id` is saved to `webhookId`.", "webhooks/managing-endpoints",
            {"url": "https://your-app.com/hooks/anakin", "description": "Production receiver", "events": ["job.completed", "job.failed"]},
            tests=capture("webhookId", "id")),
        req("List endpoints", "GET", "/webhooks", "List endpoints.", "webhooks/managing-endpoints"),
        req("Update endpoint", "PATCH", "/webhooks/{{webhookId}}", "Change events or disable an endpoint.",
            "webhooks/managing-endpoints", {"events": ["job.completed", "job.failed", "monitor.change"], "isActive": True}),
        req("Send test event", "POST", "/webhooks/{{webhookId}}/test", "Send a test event.", "webhooks/managing-endpoints"),
        req("List endpoint deliveries", "GET", "/webhooks/{{webhookId}}/deliveries", "Deliveries to one endpoint.", "webhooks/managing-endpoints"),
        req("List all deliveries", "GET", "/webhooks/deliveries", "Deliveries across endpoints.", "webhooks/managing-endpoints"),
        req("Resend delivery", "POST", "/webhooks/deliveries/{{deliveryId}}/resend", "Resend one delivery.", "webhooks/managing-endpoints"),
        req("Get signing secret", "GET", "/webhooks/signing-secret", "Secret used to sign webhook payloads.", "webhooks/managing-endpoints"),
        req("Rotate signing secret", "POST", "/webhooks/signing-secret/rotate", "Rotate the signing secret.", "webhooks/managing-endpoints"),
        req("Delete endpoint", "DELETE", "/webhooks/{{webhookId}}", "Delete an endpoint.", "webhooks/managing-endpoints"),
    ]),
]

REFERENCE_VARS = ["scrapeJobId", "agenticSearchId", "mapJobId", "crawlJobId", "wireJobId", "identityId",
                  "identitySourceId", "containerId", "providerToken", "monitorId", "snapshotId", "deliveryId",
                  "aiVisibilitySearchId", "sessionId", "webhookId"]

REFERENCE_DESC = """Every endpoint of the [Anakin](https://anakin.io) REST API: scrape any URL into Markdown, HTML or JSON, search the web, crawl and map sites, run agentic research, and call Wire actions across 940+ sites. Proxies, JavaScript rendering, anti-bot handling and CAPTCHA solving are done for you.

## Get started

1. Get an API key at [anakin.io/account](https://anakin.io/account#developer). New accounts get 300 free credits, no card required.
2. Select the **Anakin** environment and paste the key into `apiKey` (keep it as a secret value).
3. Send **URL Scraper / Scrape URL (inline)**.

No key yet? Requests marked "No API key needed" (Wire discovery, `wire-run`, inline scrape) work without one. See the **Anakin Quickstart** collection.

## Authentication

Every request sends the `X-API-Key` header (set at collection level from `{{apiKey}}`).

## Async jobs

Scrape, batch, map, crawl, agentic search and Wire tasks return a job id. Each submit request saves that id to a collection variable, so you can send the matching **Get ... result** request right after. Poll until `status` is `completed` or `failed`.

## Links

- [API reference](https://anakin.io/docs/api-reference)
- [Error responses](https://anakin.io/docs/api-reference/error-responses)
- [Pricing](https://anakin.io/pricing)
- [MCP server](https://anakin.io/docs) (`https://mcp.anakin.io/mcp`)
"""

# ---------------------------------------------------------------------------
# Overview / quickstart collection: first 200 OK with no key
# ---------------------------------------------------------------------------
QUICKSTART = [
    ("1. No key needed", "These requests run on Anakin's free, no-signup Zero Touch tier. Send them in order.", [
        req("Scrape a page to Markdown", "POST", "/url-scraper/scrape",
            "Scrape any URL and get clean Markdown back in the same response. No API key: the response carries `trial.remaining_credits` and a signup link.",
            "url-scraper/scrape", {"url": "https://example.com"}, keyless=True,
            tests=status_ok() + ["pm.test('Has markdown', () => pm.expect(pm.response.json().markdown).to.be.a('string'));"]),
        req("Find a Wire action by intent", "GET", "/wire/resolve",
            "Describe what you want in plain language; Wire returns matching `action_id`s and their params. The first `action_id` is saved to `actionId`.",
            "wire/search-actions", query=[("q", "hacker news top stories", False)], keyless=True,
            tests=status_ok() + [
                "const results = pm.response.json().results || [];",
                "pm.test('Has results', () => pm.expect(results.length).to.be.above(0));",
                "if (results.length) { pm.collectionVariables.set('actionId', results[0].action_id); }",
            ]),
        req("Run the action", "POST", "/wire-run",
            "Run a read-only Wire action synchronously with no API key. Change `params` to match the action you picked.",
            "wire", {"action_id": "hn_stories", "params": {"limit": 5}}, keyless=True,
            tests=status_ok()),
    ]),
    ("2. With your API key", "Set `apiKey` in the Anakin environment (get one at https://anakin.io/account#developer, 300 free credits).", [
        req("Search the web", "POST", "/search",
            "Web search with page content in one call.", "search/search",
            {"prompt": "latest AI developments", "limit": 3}, tests=status_ok()),
        req("Submit a crawl", "POST", "/crawl",
            "Crawl a site. The `jobId` is saved for the next request.", "crawl/submit-crawl-job",
            {"url": "https://example.com", "maxPages": 5}, tests=status_ok() + capture("crawlJobId", "jobId")),
        req("Get crawl result", "GET", "/crawl/{{crawlJobId}}",
            "Send again until `status` is `completed`.", "crawl/get-crawl-result", tests=status_ok()),
    ]),
]

QUICKSTART_DESC = """Get your first [Anakin](https://anakin.io) result in under a minute, without signing up.

Anakin is a web data API: scrape any URL into Markdown or JSON, search the web, crawl sites, and run pre-built Wire actions on 940+ sites.

**Folder 1** works with no API key: scrape a page, find a Wire action by describing what you want, and run it.

**Folder 2** needs a key. Get one at [anakin.io/account](https://anakin.io/account#developer) (300 free credits, no card), then set `apiKey` in the **Anakin** environment.

For every endpoint, fork the **Anakin API** collection. Full docs: [anakin.io/docs](https://anakin.io/docs/api-reference).
"""


def build_request(collection_key, folder, r):
    raw_path = r["path"]
    segments = [s for s in raw_path.strip("/").split("/")]
    query = [{"key": k, "value": v, **({"disabled": True} if disabled else {})} for k, v, disabled in r["query"]]
    raw = "{{baseUrl}}" + raw_path
    enabled_q = [f"{k}={v}" for k, v, d in r["query"] if not d]
    if enabled_q:
        raw += "?" + "&".join(enabled_q)
    request = {
        "method": r["method"],
        "header": [],
        "url": {"raw": raw, "host": ["{{baseUrl}}"], "path": segments, **({"query": query} if query else {})},
        "description": r["desc"] + f"\n\nDocs: [{DOCS}/{r['docs']}]({DOCS}/{r['docs']})",
    }
    if r["body"] is not None:
        request["header"].append({"key": "Content-Type", "value": "application/json"})
        request["body"] = {"mode": "raw", "raw": json.dumps(r["body"], indent=2),
                           "options": {"raw": {"language": "json"}}}
    if r["keyless"]:
        request["auth"] = {"type": "noauth"}
    item = {"id": uid(collection_key, folder, r["name"]), "name": r["name"], "request": request, "response": []}
    if r["tests"]:
        item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": r["tests"]}}]
    return item


def build_collection(key, name, desc, folders, variables):
    return {
        "info": {"_postman_id": uid(key), "name": name, "description": desc, "schema": SCHEMA},
        "auth": {"type": "apikey", "apikey": [
            {"key": "key", "value": "X-API-Key", "type": "string"},
            {"key": "value", "value": "{{apiKey}}", "type": "string"},
            {"key": "in", "value": "header", "type": "string"},
        ]},
        "variable": [{"key": "baseUrl", "value": "https://api.anakin.io/v1"},
                     {"key": "catalogSlug", "value": "hackernews"}]
                    + [{"key": v, "value": ""} for v in variables],
        "item": [{"id": uid(key, fname), "name": fname, "description": fdesc,
                  "item": [build_request(key, fname, r) for r in reqs]}
                 for fname, fdesc, reqs in folders],
    }


ENVIRONMENT = {
    "id": uid("environment"),
    "name": "Anakin",
    "values": [
        {"key": "baseUrl", "value": "https://api.anakin.io/v1", "type": "default", "enabled": True},
        {"key": "apiKey", "value": "", "type": "secret", "enabled": True},
    ],
    "_postman_variable_scope": "environment",
}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    write(ROOT / "collections/anakin-api.postman_collection.json",
          build_collection("api", "Anakin API", REFERENCE_DESC, REFERENCE, REFERENCE_VARS))
    write(ROOT / "collections/anakin-quickstart.postman_collection.json",
          build_collection("quickstart", "Anakin Quickstart", QUICKSTART_DESC, QUICKSTART, ["crawlJobId", "actionId"]))
    write(ROOT / "environments/anakin.postman_environment.json", ENVIRONMENT)
