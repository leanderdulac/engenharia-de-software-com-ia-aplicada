#!/bin/sh
# Sobe a sala só em 127.0.0.1. Não publica na rede.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
export HOST=127.0.0.1
export PORT="${PORT:-3850}"
export EAD_DATA_DIR="${EAD_DATA_DIR:-$ROOT/curso/ead/data}"
export EAD_OPEN_SIGNUP=0

node -e '
const [maj, min] = process.versions.node.split(".").map(Number);
if (maj < 22 || (maj === 22 && min < 16)) {
  console.error("Node " + process.version + " é antigo. Mínimo 22.16.0 (node:sqlite backup). Smoke deste pacote: 22.23.4.");
  process.exit(1);
}
console.log("node", process.version, "(mínimo da API 22.16.0; smoke 22.23.4)");
'

if [ ! -d "$ROOT/curso/preview/node_modules/marked" ]; then
  npm --prefix "$ROOT/curso/preview" ci
fi
if [ ! -d "$ROOT/curso/ead/node_modules/express" ]; then
  npm --prefix "$ROOT/curso/ead" ci
fi

mkdir -p "$EAD_DATA_DIR"
cd "$ROOT/curso/ead"
if [ ! -f "$EAD_DATA_DIR/ead.sqlite" ]; then
  node src/cli.mjs migrate
  if [ -z "${EAD_ADMIN_EMAIL:-}" ] || [ -z "${EAD_ADMIN_PASSWORD:-}" ]; then
    if [ ! -t 0 ]; then
      echo "Defina EAD_ADMIN_EMAIL e EAD_ADMIN_PASSWORD nesta sessão, ou rode num terminal interactivo. Não há senha padrão." >&2
      exit 1
    fi
    printf "E-mail do administrador local: "
    read -r EAD_ADMIN_EMAIL
    printf "Senha (mínimo 10, não fica no pacote): "
    stty -echo
    read -r EAD_ADMIN_PASSWORD
    stty echo
    printf "\n"
    export EAD_ADMIN_EMAIL EAD_ADMIN_PASSWORD
  fi
  node src/cli.mjs create-admin
  unset EAD_ADMIN_PASSWORD
fi

echo "Nesta máquina apenas: http://127.0.0.1:${PORT}/"
echo "Pare com Ctrl+C ou ./scripts/parar.sh"
child=""
cleanup() {
  if [ -n "$child" ]; then
    kill "$child" 2>/dev/null || true
  fi
  rm -f "$EAD_DATA_DIR/ead.pid"
}
trap cleanup INT TERM
node src/server.mjs &
child=$!
echo "$child" > "$EAD_DATA_DIR/ead.pid"
wait "$child"
rm -f "$EAD_DATA_DIR/ead.pid"
