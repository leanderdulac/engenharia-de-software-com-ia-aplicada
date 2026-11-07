#!/usr/bin/env node
/**
 * Gera um site estático do preview em curso/preview/dist/
 * para GitHub Pages (hash routing) ou inspeção local.
 *
 *   node curso/preview/build.mjs
 *
 * Não publica. Não altera settings da conta. Não regenera mídia.
 */
import { cp, mkdir, readFile, writeFile, rm } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { CURSO_ROOT, MEDIA_DIR, PUBLIC_DIR, PREVIEW_ROOT, REPO_ROOT, toPosix } from "./lib/paths.mjs";
import { ARQUIVOS_EXT_OK } from "./lib/paths.mjs";
import { renderMarkdownPage, resolveRepoFile } from "./lib/markdown.mjs";
import { extractMarkdownLinks, walkMarkdownFiles } from "./lib/links.mjs";
import { grokVideosPayload, ttsAudiosPayload } from "./server.js";

const DIST = path.join(PREVIEW_ROOT, "dist");

function pagesJsonRel(mdRel) {
  const withoutExt = mdRel.replace(/\.md$/i, "");
  return `pages/${withoutExt}.json`;
}

async function copyPdfIfNeeded(abs, relRepo, copied) {
  if (copied.has(relRepo)) return;
  copied.add(relRepo);
  const dest = path.join(DIST, "arquivos", relRepo);
  await mkdir(path.dirname(dest), { recursive: true });
  await cp(abs, dest);
}

async function collectPdfsFromMarkdown(md, mdRel, copied) {
  for (const { href } of extractMarkdownLinks(md)) {
    const resolved = resolveRepoFile(href.split(/\s+/)[0], mdRel);
    if (
      resolved &&
      resolved.kind === "relative" &&
      resolved.ext === ".pdf" &&
      resolved.insideRepo &&
      ARQUIVOS_EXT_OK.has(resolved.ext)
    ) {
      try {
        await copyPdfIfNeeded(resolved.abs, resolved.relRepo, copied);
      } catch {
        /* missing PDF is reported by check.mjs */
      }
    }
  }
}

async function write404(basePath) {
  const html = `<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <title>Redirecionando…</title>
    <script>
      (function () {
        var base = ${JSON.stringify(basePath)};
        var path = location.pathname;
        if (base && path.indexOf(base) === 0) path = path.slice(base.length);
        path = path.replace(/^\\/+/, "");
        var hash = path ? ("#/" + decodeURIComponent(path)) : "#/README.md";
        location.replace((base || "./") + hash + location.search);
      })();
    </script>
  </head>
  <body>
    <p>Abrindo o preview…</p>
  </body>
</html>
`;
  await writeFile(path.join(DIST, "404.html"), html);
}

async function injectIndex(basePath) {
  let html = await readFile(path.join(PUBLIC_DIR, "index.html"), "utf8");
  html = html.replace(
    "<head>",
    `<head>\n    <base href="${basePath}">`
  );
  html = html.replace(
    "window.__PREVIEW__ = { mode: \"live\" };",
    `window.__PREVIEW__ = { mode: "static", base: ${JSON.stringify(basePath)} };`
  );
  await writeFile(path.join(DIST, "index.html"), html);
}

async function build() {
  const repoName = process.env.GITHUB_REPOSITORY?.split("/")[1] || "";
  const basePath = process.env.PAGES_BASE
    || (process.env.GITHUB_PAGES === "1" && repoName ? `/${repoName}/` : "./");

  await rm(DIST, { recursive: true, force: true });
  await mkdir(path.join(DIST, "pages"), { recursive: true });
  await mkdir(path.join(DIST, "api"), { recursive: true });
  await mkdir(path.join(DIST, "arquivos"), { recursive: true });

  await cp(path.join(PUBLIC_DIR, "app.js"), path.join(DIST, "app.js"));
  await cp(path.join(PUBLIC_DIR, "styles.css"), path.join(DIST, "styles.css"));
  await injectIndex(basePath);
  await write404(basePath);

  await cp(MEDIA_DIR, path.join(DIST, "media"), { recursive: true });

  const copiedPdfs = new Set();
  const mdFiles = await walkMarkdownFiles(CURSO_ROOT);
  const pages = [];

  for (const abs of mdFiles) {
    const rel = toPosix(path.relative(CURSO_ROOT, abs));
    if (rel.startsWith("preview/")) continue;
    const markdown = await readFile(abs, "utf8");
    const page = renderMarkdownPage(markdown, rel);
    const outRel = pagesJsonRel(rel);
    const outAbs = path.join(DIST, outRel);
    await mkdir(path.dirname(outAbs), { recursive: true });
    await writeFile(outAbs, JSON.stringify(page));
    pages.push(rel);
    await collectPdfsFromMarkdown(markdown, rel, copiedPdfs);
  }

  await writeFile(
    path.join(DIST, "api", "grok-videos.json"),
    JSON.stringify(await grokVideosPayload())
  );
  await writeFile(
    path.join(DIST, "api", "tts-audios.json"),
    JSON.stringify(await ttsAudiosPayload())
  );

  const manifest = {
    generated_at: new Date().toISOString(),
    mode: "static",
    base: basePath,
    pages: pages.sort(),
    pdfs: [...copiedPdfs].sort(),
    aviso:
      "Build local/CI. Não implica Pages habilitado nem autorização jurídica para publicar adaptações.",
  };
  await writeFile(path.join(DIST, "manifest.json"), JSON.stringify(manifest, null, 2));

  console.log(`Preview estático em ${DIST}`);
  console.log(`base=${basePath} páginas=${pages.length} pdfs=${copiedPdfs.size}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  build().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

export { build, DIST };
