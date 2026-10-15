#!/bin/sh
# Run the collections against the live API.
# Without ANAKIN_API_KEY: only the keyless requests (free Zero Touch tier).
# With ANAKIN_API_KEY: also the keyed quickstart folder (uses a few credits).
set -e
cd "$(dirname "$0")/.."
NEWMAN="npx --yes newman@6"
ENV=environments/anakin.postman_environment.json

$NEWMAN run collections/anakin-quickstart.postman_collection.json -e "$ENV" --folder "1. No key needed"
$NEWMAN run collections/anakin-api.postman_collection.json -e "$ENV" --folder "Wire / Discovery"

if [ -n "$ANAKIN_API_KEY" ]; then
  $NEWMAN run collections/anakin-quickstart.postman_collection.json -e "$ENV" \
    --env-var "apiKey=$ANAKIN_API_KEY" --folder "2. With your API key"
else
  echo "ANAKIN_API_KEY not set: skipped keyed requests."
fi
