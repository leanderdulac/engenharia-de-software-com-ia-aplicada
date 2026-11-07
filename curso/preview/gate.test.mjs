import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { after, describe, it } from "node:test";
import { openDb, nowIso } from "../ead/src/db.mjs";
import { createSession, hashPassword } from "../ead/src/auth.mjs";
import { assertPreviewListen, resetPreviewGate } from "./lib/gate.mjs";
import { createApp } from "./server.js";

describe("portão do preview", () => {
  after(() => {
    delete process.env.PREVIEW_REQUIRE_AUTH;
    delete process.env.PREVIEW_AUTH_DB;
    resetPreviewGate();
  });

  it("produção sem flag ou sem base falha fechado", () => {
    assert.throws(() => assertPreviewListen({ NODE_ENV: "production" }));
    assert.throws(() =>
      assertPreviewListen({ NODE_ENV: "production", PREVIEW_REQUIRE_AUTH: "1" })
    );
    assert.doesNotThrow(() =>
      assertPreviewListen({
        NODE_ENV: "production",
        PREVIEW_REQUIRE_AUTH: "1",
        EAD_DATA_DIR: "/var/ead",
      })
    );
    assert.doesNotThrow(() => assertPreviewListen({}));
  });

  it("sem cookie recusa página, API, mídia e markdown; com ead_sid entrega", async () => {
    const dir = mkdtempSync(path.join(tmpdir(), "preview-gate-"));
    const dbPath = path.join(dir, "ead.sqlite");
    process.env.PREVIEW_REQUIRE_AUTH = "1";
    process.env.PREVIEW_AUTH_DB = dbPath;
    resetPreviewGate();

    const db = openDb(dbPath);
    const info = db
      .prepare(
        "INSERT INTO users (email, password_hash, name, role, demo, diagnostic_done, created_at) VALUES (?, ?, ?, 'aluno', 0, 0, ?)"
      )
      .run("aluno.gate@local.test", hashPassword("Aluno-Gate-teste-10"), "Aluno gate", nowIso());
    const { token } = createSession(db, Number(info.lastInsertRowid));

    const app = createApp();
    const server = await new Promise((resolve) => {
      const httpd = app.listen(0, "127.0.0.1", () => resolve(httpd));
    });
    const base = `http://127.0.0.1:${server.address().port}`;
    try {
      for (const pathName of ["/", "/api/page?path=README.md", "/media/imagens/curso-capa-hero.png", "/README.md?raw=1"]) {
        const anon = await fetch(base + pathName);
        assert.equal(anon.status, 401, pathName);
        await anon.text();
      }
      const css = await fetch(base + "/styles.css");
      assert.equal(css.status, 200);
      await css.text();

      const cookie = { cookie: `ead_sid=${token}` };
      const home = await fetch(base + "/", { headers: cookie });
      assert.equal(home.status, 200);
      assert.match(await home.text(), /<html/i);
      const page = await fetch(base + "/api/page?path=README.md", { headers: cookie });
      assert.equal(page.status, 200);
      const media = await fetch(base + "/media/imagens/curso-capa-hero.png", { headers: cookie });
      assert.equal(media.status, 200);
      assert.match(media.headers.get("content-type") || "", /image\//);
      await media.arrayBuffer();
    } finally {
      await new Promise((resolve) => server.close(resolve));
      db.close();
    }
  });

  it("Host alheio e path codificado não contornam o portão", async () => {
    const http = await import("node:http");
    const dir = mkdtempSync(path.join(tmpdir(), "preview-host-"));
    const dbPath = path.join(dir, "ead.sqlite");
    process.env.PREVIEW_REQUIRE_AUTH = "1";
    process.env.PREVIEW_AUTH_DB = dbPath;
    resetPreviewGate();
    const db = openDb(dbPath);
    const info = db
      .prepare(
        "INSERT INTO users (email, password_hash, name, role, demo, diagnostic_done, created_at) VALUES (?, ?, ?, 'aluno', 0, 0, ?)"
      )
      .run("gate2@local.test", hashPassword("Aluno-Gate-teste-10"), "Gate", nowIso());
    const { token } = createSession(db, Number(info.lastInsertRowid));
    const app = createApp();
    const server = await new Promise((resolve) => {
      const httpd = app.listen(0, "127.0.0.1", () => resolve(httpd));
    });
    const port = server.address().port;
    try {
      const status = await new Promise((resolve, reject) => {
        const req = http.request({ hostname: "127.0.0.1", port, path: "/api/page?path=README.md", headers: { host: "evil.example" } }, (res) => {
          res.resume();
          resolve(res.statusCode);
        });
        req.on("error", reject);
        req.end();
      });
      assert.equal(status, 421);
      const bypass = await fetch(`http://127.0.0.1:${port}/api/page?path=%2e%2e/package.json`, {
        headers: { cookie: `ead_sid=${token}` },
      });
      assert.notEqual(bypass.status, 200);
      const body = await bypass.text();
      assert.equal(body.includes("scrypt"), false);
      assert.equal(body.includes("EAD_ADMIN"), false);
    } finally {
      await new Promise((resolve) => server.close(resolve));
      db.close();
    }
  });
});
