import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { DEMO, csrfFrom, grab, Jar, login } from "./helpers.mjs";
import { boot } from "../src/server.mjs";
import { listenApp } from "./helpers.mjs";

test("progresso persiste após fechar e reabrir o SQLite", async (t) => {
  const dir = mkdtempSync(path.join(tmpdir(), "ead-persist-"));
  const dbPath = path.join(dir, "ead.sqlite");
  const first = boot({
    dbPath,
    seedDemoPasswords: { instructor: DEMO.instructor, alunoA: DEMO.alunoA, alunoB: DEMO.alunoB },
  });
  const { server, origin } = await listenApp(first.app);
  const jar = new Jar();
  await login(origin, jar, "aluno-a.demo@local.test", DEMO.alunoA);
  const cat = await grab(origin, jar, "/catalogo");
  await grab(origin, jar, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(cat.text) }),
  });
  const aula = await grab(origin, jar, "/aula/m01-aula");
  await grab(origin, jar, "/aula/m01-aula/concluir", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(aula.text) }),
  });
  server.close();
  first.db.close();

  const second = boot({ dbPath });
  t.after(() => second.db.close());
  const row = second.db
    .prepare(
      "SELECT completed FROM lesson_progress WHERE lesson_id = 'm01-aula' AND user_id = (SELECT id FROM users WHERE email = ?)"
    )
    .get("aluno-a.demo@local.test");
  assert.equal(row?.completed, 1);
});
