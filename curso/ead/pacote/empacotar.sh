#!/bin/sh
# Monta o arquivo localhost a partir da árvore de trabalho. Não inclui git, deps, base nem segredos.
set -eu
REPO=$(CDPATH= cd -- "$(dirname "$0")/../../.." && pwd)
STAGE=$(mktemp -d)
DEST="$STAGE/lms-localhost"
OUT="${1:-/opt/cursor/artifacts}"
mkdir -p "$OUT" "$DEST/scripts" "$DEST/curso/preview/lib" "$DEST/curso/preview/public" "$DEST/curso/piloto" "$DEST/referencia"

mkdir -p "$DEST/curso/ead"
tar -C "$REPO/curso/ead" \
  --exclude node_modules \
  --exclude data \
  --exclude tests \
  --exclude e2e.mjs \
  --exclude pacote \
  --exclude .env \
  --exclude .env.local \
  --exclude .env.production \
  -cf - . | tar -C "$DEST/curso/ead" -xf -

cp "$REPO/curso/preview/package.json" "$REPO/curso/preview/package-lock.json" "$REPO/curso/preview/server.js" "$DEST/curso/preview/"
cp "$REPO/curso/preview/lib/"*.mjs "$DEST/curso/preview/lib/"
cp "$REPO/curso/preview/public/"* "$DEST/curso/preview/public/"

cp -a "$REPO/curso/conteudo" "$REPO/curso/modulos" "$REPO/curso/media" "$DEST/curso/"
cp "$REPO/curso/avaliacao.md" "$REPO/curso/glossario.md" "$DEST/curso/"
cp "$REPO/curso/piloto/pre-pos-teste.md" "$DEST/curso/piloto/"
mkdir -p "$DEST/curso/avaliacao-colaboracao" "$DEST/referencia/llm-course"
tar -C "$REPO/curso/avaliacao-colaboracao" --exclude verificar.test.mjs -cf - . | tar -C "$DEST/curso/avaliacao-colaboracao" -xf -
tar -C "$REPO/referencia/llm-course" --exclude .git -cf - . | tar -C "$DEST/referencia/llm-course" -xf -

cd "$REPO"
find \
  modulo07-ferramentas-de-ia-para-gestao-de-projetos \
  modulo08-arquitetura-de-sistemas-com-ia \
  modulo09-processamento-de-dados-e-fine-tuning-de-modelos \
  -iname 'Atividade*.pdf' -print | while IFS= read -r rel; do
  mkdir -p "$DEST/$(dirname "$rel")"
  cp "$REPO/$rel" "$DEST/$rel"
done

cp "$REPO/curso/ead/pacote/README-LOCAL.md" "$DEST/README-LOCAL.md"
cp "$REPO/curso/ead/pacote/scripts/"*.sh "$DEST/scripts/"
chmod +x "$DEST/scripts/"*.sh

if find "$DEST" \( -name node_modules -o -name '.git' -o -name '.env' -o -name 'ead.sqlite' -o -name '*.sqlite' \) -print | grep -q .; then
  echo "pacote recusado: contém dependência, git, env ou base" >&2
  find "$DEST" \( -name node_modules -o -name '.git' -o -name '.env' -o -name 'ead.sqlite' \) -print >&2
  exit 1
fi

{
  echo "lms-localhost"
  echo "node_api_minimo 22.16.0"
  echo "node_smoke 22.23.4"
  echo "gerado $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "ficheiros $(find "$DEST" -type f | wc -l)"
} > "$DEST/MANIFEST.txt"

tar -C "$STAGE" -czf "$OUT/lms-localhost.tar.gz" lms-localhost
python3 - "$STAGE" "$OUT/lms-localhost.zip" <<'PY'
import os, sys, zipfile
stage, dest = sys.argv[1], sys.argv[2]
root = os.path.join(stage, "lms-localhost")
with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as z:
    for dirpath, _, names in os.walk(root):
        for name in names:
            full = os.path.join(dirpath, name)
            z.write(full, os.path.relpath(full, stage))
PY

rm -rf "$STAGE"
echo "tar $OUT/lms-localhost.tar.gz"
echo "zip $OUT/lms-localhost.zip"
sha256sum "$OUT/lms-localhost.tar.gz" "$OUT/lms-localhost.zip"
