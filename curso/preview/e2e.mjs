#!/usr/bin/env node
/**
 * Dry-run de navegação headless do preview (Chrome via DevTools).
 * Não valida aprendizagem de alunos.
 *
 *   node curso/preview/e2e.mjs
 */
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import path from "node:path";
import { createApp } from "./server.js";

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    "/usr/local/bin/google-chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ].filter(Boolean);
  for (const bin of candidates) {
    const r = spawnSync(bin, ["--version"], { encoding: "utf8" });
    if (r.status === 0) return bin;
  }
  return null;
}

function freePort() {
  return new Promise((resolve, reject) => {
    const s = createServer();
    s.listen(0, "127.0.0.1", () => {
      const { port } = s.address();
      s.close((err) => (err ? reject(err) : resolve(port)));
    });
    s.on("error", reject);
  });
}

async function waitForWs(port, timeoutMs = 20000) {
  const start = Date.now();
  let lastErr;
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) {
        const data = await res.json();
        if (data.webSocketDebuggerUrl) return data.webSocketDebuggerUrl;
      }
    } catch (err) {
      lastErr = err;
    }
    await new Promise((resolve) => setTimeout(resolve, 150));
  }
  throw new Error(`Chrome CDP não arrancou em 127.0.0.1:${port}: ${lastErr?.message || "sem /json/version"}`);
}

async function spawnChrome(chrome) {
  const port = await freePort();
  const profile = mkdtempSync(path.join(tmpdir(), "curso-preview-e2e-"));
  const child = spawn(
    chrome,
    [
      "--headless=new",
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      `--user-data-dir=${profile}`,
      `--remote-debugging-port=${port}`,
      "--remote-allow-origins=*",
      "about:blank",
    ],
    { stdio: ["ignore", "ignore", "pipe"] }
  );
  child.__profile = profile;
  try {
    const wsUrl = await waitForWs(port);
    return { child, wsUrl, profile };
  } catch (err) {
    child.kill("SIGKILL");
    rmSync(profile, { recursive: true, force: true });
    throw err;
  }
}

class Cdp {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 0;
    this.pending = new Map();
    this.ws.addEventListener("message", (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id != null && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
        else resolve(msg.result);
      }
    });
  }

  ready() {
    if (this.ws.readyState === WebSocket.OPEN) return Promise.resolve();
    return new Promise((resolve, reject) => {
      this.ws.addEventListener("open", () => resolve(), { once: true });
      this.ws.addEventListener("error", (err) => reject(err), { once: true });
    });
  }

  send(method, params = {}, sessionId) {
    const id = ++this.nextId;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`CDP timeout: ${method}`));
        }
      }, 15000);
    });
  }

  close() {
    try {
      this.ws.close();
    } catch {
      /* ignore */
    }
  }
}

async function openPage(cdp, url) {
  const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.send("Target.attachToTarget", {
    targetId,
    flatten: true,
  });
  await cdp.send("Page.enable", {}, sessionId);
  await cdp.send("Runtime.enable", {}, sessionId);
  await cdp.send("Page.navigate", { url }, sessionId);
  return { sessionId, targetId };
}

async function evaluate(cdp, sessionId, expression) {
  const result = await cdp.send(
    "Runtime.evaluate",
    { expression, returnByValue: true, awaitPromise: true },
    sessionId
  );
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || "Runtime.evaluate falhou");
  }
  return result.result?.value;
}

async function waitFor(cdp, sessionId, expression, timeoutMs = 10000) {
  const start = Date.now();
  let last;
  while (Date.now() - start < timeoutMs) {
    last = await evaluate(cdp, sessionId, expression);
    if (last) return last;
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error(`timeout à espera de: ${expression} (último=${JSON.stringify(last)?.slice(0, 180)})`);
}

async function main() {
  const chrome = findChrome();
  if (!chrome) {
    console.log("SKIP  Chrome/Chromium não encontrado — e2e omitido");
    process.exit(0);
  }
  console.log(`OK    chrome ${chrome}`);

  const app = createApp();
  const server = await new Promise((resolve) => {
    const s = app.listen(0, "127.0.0.1", () => resolve(s));
  });
  const port = server.address().port;
  const origin = `http://127.0.0.1:${port}`;
  const failures = [];

  const source = await (await fetch(origin)).text();
  if (!source.includes('href="./styles.css"')) {
    failures.push("shell sem href=\"./styles.css\"");
    console.error("FAIL  shell CSS relativo");
  } else if (!source.includes('src="./app.js"')) {
    failures.push("shell sem src=\"./app.js\"");
    console.error("FAIL  shell JS relativo");
  } else if (!source.includes("Pular para o conteúdo")) {
    failures.push("shell sem skip-link");
    console.error("FAIL  skip-link");
  } else {
    console.log("OK    shell HTML: CSS/JS relativos e skip-link");
  }

  let chromeProc;
  let chromeProfile;
  try {
    const launched = await spawnChrome(chrome);
    chromeProc = launched.child;
    chromeProfile = launched.profile;
    const cdp = new Cdp(launched.wsUrl);
    await cdp.ready();

    async function step(name, url, checkExpr, extraFn) {
      try {
        const { sessionId, targetId } = await openPage(cdp, url);
        await waitFor(cdp, sessionId, checkExpr);
        if (extraFn) await extraFn(cdp, sessionId);
        console.log(`OK    ${name}`);
        await cdp.send("Target.closeTarget", { targetId }).catch(() => null);
      } catch (err) {
        failures.push(`${name}: ${err.message}`);
        console.error(`FAIL  ${name}: ${err.message}`);
      }
    }

    await step(
      "home renderiza o pacote",
      origin,
      `document.querySelector("#article") && /syllabus|guia|módulo|modulo/i.test(document.querySelector("#article").innerText) && !!document.querySelector('link[href*="styles.css"]')`
    );

    await step(
      "hash módulo 01 renderiza o h1",
      `${origin}/#/modulos/01.md`,
      `!!document.querySelector("#article") && /M[oó]dulo 01/i.test(document.querySelector("#article").innerText)`,
      async (cdp, sessionId) => {
        const href = await evaluate(
          cdp,
          sessionId,
          `document.querySelector('link[rel="stylesheet"]')?.getAttribute("href") || ""`
        );
        if (!/styles\.css/.test(href)) throw new Error(`CSS perdido na rota hash (href=${href})`);
      }
    );

    await step(
      "aula profunda + recarga",
      `${origin}/#/conteudo/modulo-01/aula.md`,
      `!!document.querySelector("#article") && /M[oó]dulo 01/i.test(document.querySelector("#article").innerText) && !document.body.innerText.includes("<h1># ")`,
      async (cdp, sessionId) => {
        await cdp.send("Page.reload", { ignoreCache: true }, sessionId);
        await waitFor(
          cdp,
          sessionId,
          `!!document.querySelector("#article") && /M[oó]dulo 01/i.test(document.querySelector("#article").innerText)`
        );
      }
    );

    await step(
      "aprofundamento Apache isolado",
      `${origin}/#/ATRIBUICOES-llm-course.md`,
      `!!document.querySelector("#article") && /Apache/i.test(document.querySelector("#article").innerText)`
    );

    cdp.close();
  } catch (err) {
    failures.push(`chrome: ${err.message}`);
    console.error(`FAIL  chrome: ${err.message}`);
  } finally {
    if (chromeProc) chromeProc.kill("SIGKILL");
    if (chromeProfile) rmSync(chromeProfile, { recursive: true, force: true });
    await new Promise((resolve) => server.close(resolve));
  }

  if (failures.length) {
    console.error(`e2e falhou: ${failures.length}`);
    process.exit(1);
  }
  console.log("e2e preview: pass (dry-run técnico; não valida aprendizagem)");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
