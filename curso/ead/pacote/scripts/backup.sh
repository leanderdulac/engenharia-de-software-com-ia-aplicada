#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
export EAD_DATA_DIR="${EAD_DATA_DIR:-$ROOT/curso/ead/data}"
stamp=$(date +%F)
dest="$EAD_DATA_DIR/backup-${stamp}.sqlite"
cd "$ROOT/curso/ead"
node src/cli.mjs backup "$dest"
echo "cópia em $dest"
echo "para repor: pare a sala e rode, em curso/ead,"
echo "  EAD_DATA_DIR=\"\$PWD/data\" node src/cli.mjs restore data/backup-${stamp}.sqlite"
