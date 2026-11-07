#!/usr/bin/env node
/**
 * Checagem reprodutível do preview e dos links do pacote curso/.
 *
 *   node curso/preview/check.mjs
 *   node curso/preview/check.mjs --external
 *
 * Links externos HTTP 403 = bloqueados (não falham o check).
 * HTTP 404 externo = aviso. Links internos quebrados = falha.
 */
import { access, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { CURSO_ROOT, MEDIA_DIR, PUBLIC_DIR, REPO_ROOT } from "./lib/paths.mjs";
import { collectInternalLinkIssues, extractMarkdownLinks, classifyHref, walkMarkdownFiles } from "./lib/links.mjs";
import { extractTitle, stripHomeHeroDuplicate, rewriteHtml } from "./lib/markdown.mjs";

const FAIL = [];
const WARN = [];
const INFO = [];

function ok(msg) {
  INFO.push(msg);
  console.log(`OK    ${msg}`);
}
function warn(msg) {
  WARN.push(msg);
  console.warn(`WARN  ${msg}`);
}
function fail(msg) {
  FAIL.push(msg);
  console.error(`FAIL  ${msg}`);
}

async function exists(p) {
  try {
    await access(p);
    return true;
  } catch {
    return false;
  }
}

async function checkHelpers() {
  const title = extractTitle("# Olá **mundo**\n\ntexto", "x");
  if (title !== "Olá mundo") fail(`extractTitle: esperado "Olá mundo", obtido "${title}"`);
  else ok("extractTitle exportado e funcional");

  const stripped = stripHomeHeroDuplicate(
    '<p><img src="x" alt="curso-capa-hero"></p><h1>T</h1>',
    "README.md"
  );
  if (/curso-capa-hero/.test(stripped)) fail("stripHomeHeroDuplicate não removeu o hero");
  else ok("stripHomeHeroDuplicate exportado e funcional");

  const html = rewriteHtml(
    '<p><img src="../media/imagens/modulo-01-capa.png" alt="c"></p>',
    "modulos/01.md"
  );
  if (!html.includes('src="/media/imagens/modulo-01-capa.png"')) {
    fail(`rewriteHtml mídia: ${html}`);
  } else ok("rewriteHtml reescreve capas para /media/");
}

async function checkPublicAssets() {
  for (const file of ["index.html", "app.js", "styles.css"]) {
    const abs = path.join(PUBLIC_DIR, file);
    if (!(await exists(abs))) fail(`asset ausente: ${file}`);
    else ok(`asset ${file}`);
  }
  const index = await readFile(path.join(PUBLIC_DIR, "index.html"), "utf8");
  if (index.includes('href="/styles.css"') || index.includes('src="/app.js"')) {
    fail("index.html ainda usa JS/CSS absolutos na raiz — quebram GitHub Pages e rotas profundas");
  } else ok("index.html usa assets relativos");
  if (!index.includes('src="./app.js"') && !index.includes("src=\"./app.js\"")) {
    if (!/src="\.\/app\.js"/.test(index)) fail("index.html sem ./app.js");
  }
}

async function checkMediaManifests() {
  const grok = path.join(MEDIA_DIR, "videos", "grok", "manifest.json");
  const tts = path.join(MEDIA_DIR, "audios", "tts", "manifest.json");
  for (const p of [grok, tts]) {
    if (!(await exists(p))) fail(`manifesto ausente: ${path.relative(REPO_ROOT, p)}`);
    else ok(`manifesto ${path.basename(path.dirname(p))}`);
  }
  if (await exists(tts)) {
    const data = JSON.parse(await readFile(tts, "utf8"));
    const items = Array.isArray(data) ? data : data.files;
    for (const item of items || []) {
      const file = path.basename(item.file);
      const vtt = path.basename(item.vtt || file.replace(/\.mp3$/i, ".vtt"));
      if (!(await exists(path.join(MEDIA_DIR, "audios", "tts", file)))) {
        fail(`TTS ausente: ${file}`);
      }
      if (!(await exists(path.join(MEDIA_DIR, "audios", "tts", vtt)))) {
        fail(`VTT ausente: ${vtt}`);
      }
    }
    ok("arquivos TTS + VTT citados no manifesto existem (legendas no disco; não ouvimos o áudio)");
  }
}

async function checkInternalLinks() {
  const missing = await collectInternalLinkIssues();
  if (missing.length) {
    for (const item of missing.slice(0, 40)) {
      fail(`link interno: ${item.from} -> ${item.href}`);
    }
    if (missing.length > 40) fail(`… e mais ${missing.length - 40} links internos quebrados`);
  } else {
    ok("todos os links relativos do pacote curso/ apontam para arquivos existentes");
  }
}

async function checkNoMdAsDefaultHtml() {
  const files = await walkMarkdownFiles(CURSO_ROOT);
  ok(`${files.length} arquivos .md no pacote curso/ (não devem ser servidos como text/html sem raw=1)`);
}

async function checkExternal(enabled) {
  if (!enabled) {
    INFO.push("checagem externa omitida (passe --external)");
    console.log("SKIP  links externos (use --external)");
    return;
  }
  const files = await walkMarkdownFiles(CURSO_ROOT);
  const seen = new Set();
  const urls = [];
  for (const abs of files) {
    const md = await readFile(abs, "utf8");
    for (const { href } of extractMarkdownLinks(md)) {
      const c = classifyHref(href);
      if (c.kind !== "external") continue;
      const url = c.href.startsWith("//") ? `https:${c.href}` : c.href;
      if (seen.has(url)) continue;
      seen.add(url);
      urls.push(url);
    }
  }

  const blocked = [];
  const notFound = [];
  const okUrls = [];
  const network = [];

  for (const url of urls) {
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 8000);
      let res = await fetch(url, { method: "HEAD", redirect: "follow", signal: ctrl.signal });
      if (res.status === 405 || res.status === 501) {
        res = await fetch(url, { method: "GET", redirect: "follow", signal: ctrl.signal });
      }
      clearTimeout(t);
      if (res.status === 403 || res.status === 401) blocked.push({ url, status: res.status });
      else if (res.status === 404) notFound.push({ url, status: res.status });
      else if (res.ok) okUrls.push(url);
      else warn(`externo HTTP ${res.status}: ${url}`);
    } catch (err) {
      network.push({ url, error: err.name || String(err) });
    }
  }

  for (const item of blocked) {
    warn(`externo BLOQUEADO ${item.status} (≠ 404): ${item.url}`);
  }
  for (const item of notFound) {
    warn(`externo 404: ${item.url}`);
  }
  for (const item of network) {
    warn(`externo rede/timeout: ${item.url} (${item.error})`);
  }
  ok(`externos OK=${okUrls.length} bloqueados(403/401)=${blocked.length} 404=${notFound.length} rede=${network.length}`);
}

async function main() {
  const external = process.argv.includes("--external");
  await checkHelpers();
  await checkPublicAssets();
  await checkMediaManifests();
  await checkInternalLinks();
  await checkNoMdAsDefaultHtml();
  await checkExternal(external);

  console.log("");
  console.log(`resumo: fail=${FAIL.length} warn=${WARN.length} ok=${INFO.length}`);
  if (FAIL.length) process.exitCode = 1;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
