# Anakin for Postman

Postman collections for the [Anakin](https://anakin.io) web data API, published to the
[Postman API Network](https://www.postman.com/explore).

| File | What it is |
|---|---|
| `collections/anakin-api.postman_collection.json` | **Anakin API**: API reference collection, every endpoint (70 requests in 13 folders) |
| `collections/anakin-quickstart.postman_collection.json` | **Anakin Quickstart**: overview collection, first 200 OK with no API key |
| `environments/anakin.postman_environment.json` | `baseUrl` and `apiKey` (secret) |
| `scripts/build.py` | Generates all three files. Edit it, not the JSON. |
| `scripts/test.sh` | Runs the collections against the live API with newman |

## Use it

Import the two collections and the environment into Postman (**Import** → drop the files),
select the **Anakin** environment, and send **Anakin Quickstart → 1. No key needed**.
For keyed requests, put your key (from [anakin.io/account](https://anakin.io/account#developer),
300 free credits) in `apiKey`.

Auth is the `X-API-Key` header, set once at collection level. Requests that work without a
key (inline scrape, Wire discovery, `wire-run`) override it with **No Auth**. Submit requests
for async jobs save the returned job id to a collection variable, so the matching
**Get ... result** request works right after.

## Change it

```sh
python3 scripts/build.py      # regenerate collections + environment
npm test                      # keyless live run
ANAKIN_API_KEY=ask_... npm test   # plus the keyed quickstart folder (a few credits)
```

Endpoints come from the [API reference](https://anakin.io/docs/api-reference)
([plain text](https://anakin.io/llms-full.txt)). When an endpoint changes, update
`REFERENCE` in `scripts/build.py`, rebuild, and re-import (or sync, see `SUBMIT.md`).
