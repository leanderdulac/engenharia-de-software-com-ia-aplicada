#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
PIDFILE="${EAD_DATA_DIR:-$ROOT/curso/ead/data}/ead.pid"
if [ ! -f "$PIDFILE" ]; then
  echo "Nenhum pid em $PIDFILE. Se a sala foi iniciada noutro terminal, use Ctrl+C lá." >&2
  exit 1
fi
kill "$(cat "$PIDFILE")"
rm -f "$PIDFILE"
echo "pedido de paragem enviado"
