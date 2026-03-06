#!/bin/sh
set -e

echo "Running PocketBase migrations..."
/pb/pocketbase migrate up

echo "Upserting superuser..."
/pb/pocketbase superuser upsert "$POCKETBASE_SUPERUSER_EMAIL" "$POCKETBASE_SUPERUSER_PASSWORD"

echo "Starting PocketBase server..."
exec /pb/pocketbase serve --http=0.0.0.0:8090
