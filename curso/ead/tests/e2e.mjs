#!/usr/bin/env node
/**
 * Navegação Chrome da sala EaD. Contas DEMONSTRAÇÃO/TESTE.
 * Screenshots: /opt/cursor/artifacts — não são alunos reais.
 */
import { spawn, spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { DEMO, listenApp } from "./helpers.mjs";
import { boot } from "../src/server.mjs";

const ART = process.env.EAD_ARTIFACTS || "/opt/cursor/artifacts";

function findChrome() {
  for (const bin of [
    process.env.CHROME_PATH,
    "/usr/local/bin/google-chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
  ].filter(Boolean)) {
    const r = spawnSync(bin, ["--version"], { encoding: "utf8" });
    if (r.status === 0) return bin;
  }
  return null;
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
      }, 20000);
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

async function spawnChrome(chrome) {
  const profile = mkdtempSync(path.join(tmpdir(), "ead-e2e-"));
  const port = 9400 + Math.floor(Math.random() * 80);
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
  const t0 = Date.now();
  while (Date.now() - t0 < 20000) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) {
        const j = await res.json();
        return { child, wsUrl: j.webSocketDebuggerUrl, profile };
      }
    } catch {
      /* wait */
    }
    await new Promise((r) => setTimeout(r, 150));
  }
  child.kill();
  throw new Error("Chrome CDP não arrancou");
}

async function openPage(cdp, url) {
  const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.send("Target.attachToTarget", { targetId, flatten: true });
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

async function waitFor(cdp, sessionId, expression, timeoutMs = 12000) {
  const start = Date.now();
  let last;
  while (Date.now() - start < timeoutMs) {
    last = await evaluate(cdp, sessionId, expression);
    if (last) return last;
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error(`timeout: ${expression} (último=${JSON.stringify(last)?.slice(0, 180)})`);
}

async function shot(cdp, sessionId, file, { width, height }) {
  await cdp.send(
    "Emulation.setDeviceMetricsOverride",
    { width, height, deviceScaleFactor: 1, mobile: width < 800 },
    sessionId
  );
  await new Promise((r) => setTimeout(r, 200));
  const { data } = await cdp.send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false }, sessionId);
  mkdirSync(ART, { recursive: true });
  const dest = path.join(ART, file);
  writeFileSync(dest, Buffer.from(data, "base64"));
  console.log("OK   screenshot", dest, Buffer.from(data, "base64").length, "bytes");
}

const chrome = findChrome();
if (!chrome) {
  console.log("SKIP  Chrome ausente — e2e visual não correu");
  process.exit(0);
}

const dir = mkdtempSync(path.join(tmpdir(), "ead-e2e-db-"));
const { app, db } = boot({
  dbPath: path.join(dir, "ead.sqlite"),
  seedDemoPasswords: {
    instructor: DEMO.instructor,
    alunoA: DEMO.alunoA,
    alunoB: DEMO.alunoB,
  },
});
const { server, origin } = await listenApp(app);
const html = await (await fetch(origin)).text();
if (!html.includes("Sala de aula local")) {
  console.error("FAIL  HTTP home sem título");
  process.exit(1);
}
console.log("OK   HTTP home");

let chromeProc;
let cdp;
try {
  chromeProc = await spawnChrome(chrome);
  cdp = new Cdp(chromeProc.wsUrl);
  await cdp.ready();
  console.log("OK   chrome", origin);

  const home = await openPage(cdp, origin + "/");
  await waitFor(cdp, home.sessionId, `document.body && /Sala de aula local/.test(document.body.innerText)`);
  await shot(cdp, home.sessionId, "ead-desktop-inicio.png", { width: 1280, height: 800 });
  await shot(cdp, home.sessionId, "ead-mobile-inicio.png", { width: 390, height: 844 });

  const entrar = await openPage(cdp, origin + "/entrar");
  await waitFor(cdp, entrar.sessionId, `document.querySelector('#f-email')`);
  await evaluate(
    cdp,
    entrar.sessionId,
    `(() => {
      document.querySelector('#f-email').value = ${JSON.stringify("aluno-a.demo@local.test")};
      document.querySelector('#f-password').value = ${JSON.stringify(DEMO.alunoA)};
      document.querySelector('form').submit();
      return true;
    })()`
  );
  await waitFor(
    cdp,
    entrar.sessionId,
    `location.pathname === '/dashboard' || /Continuar|diagnóstico|Catálogo/i.test(document.body.innerText)`
  );
  await shot(cdp, entrar.sessionId, "ead-desktop-painel.png", { width: 1280, height: 800 });

  await cdp.send("Page.navigate", { url: origin + "/catalogo" }, entrar.sessionId);
  await waitFor(cdp, entrar.sessionId, `/Catálogo|Matricular|M01/.test(document.body.innerText)`);
  await evaluate(cdp, entrar.sessionId, `(() => { const f = document.querySelector('form[action="/matricular"]'); if (f) f.submit(); return true; })()`);
  await new Promise((r) => setTimeout(r, 500));
  await cdp.send("Page.navigate", { url: origin + "/catalogo" }, entrar.sessionId);
  await waitFor(cdp, entrar.sessionId, `/M01/.test(document.body.innerText)`);
  await shot(cdp, entrar.sessionId, "ead-desktop-catalogo.png", { width: 1280, height: 800 });
  await shot(cdp, entrar.sessionId, "ead-mobile-catalogo.png", { width: 390, height: 844 });

  await cdp.send("Page.navigate", { url: origin + "/aula/m01-aula" }, entrar.sessionId);
  await waitFor(cdp, entrar.sessionId, `/Módulo 01|Fundamentos/.test(document.body.innerText)`);
  await shot(cdp, entrar.sessionId, "ead-desktop-aula.png", { width: 1280, height: 900 });

  await cdp.send("Page.navigate", { url: origin + "/ajuda" }, entrar.sessionId);
  await waitFor(cdp, entrar.sessionId, `/Ajuda técnica/.test(document.body.innerText)`);
  await shot(cdp, entrar.sessionId, "ead-desktop-ajuda.png", { width: 1280, height: 800 });
} finally {
  cdp?.close();
  chromeProc?.child.kill();
  if (chromeProc?.profile) {
    try {
      rmSync(chromeProc.profile, { recursive: true, force: true });
    } catch {
      /* ignore */
    }
  }
  server.close();
  try {
    db.close();
  } catch {
    /* ignore */
  }
}
