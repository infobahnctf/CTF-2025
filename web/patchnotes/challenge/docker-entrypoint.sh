#!/bin/sh
set -e

mkdir -p /tmp/data
cp -R /app/data/. /tmp/data/ 2>/dev/null || true

chown -R ctfuser:ctf "/tmp/data" || true
chmod -R 0700 "/tmp/data" || true

exec su-exec ctfuser "$@"
