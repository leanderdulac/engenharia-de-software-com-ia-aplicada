import { test } from "node:test";
import assert from "node:assert/strict";
import { DEMO, csrfFrom, follow, grab, Jar, login, startHarness } from "./helpers.mjs";

test("aluno não acede a /admin e não vê nota do outro", async (t) => {
  const { origin } = await startHarness(t);
  const ja = new Jar();
  const jb = new Jar();

  const la = await login(origin, ja, "aluno-a.demo@local.test", DEMO.alunoA);
  assert.equal(la.res.status, 303);
  await follow(origin, ja, "/dashboard");

  const lb = await login(origin, jb, "aluno-b.demo@local.test", DEMO.alunoB);
  assert.equal(lb.res.status, 303);
  await follow(origin, jb, "/dashboard");

  const admin = await grab(origin, ja, "/admin");
  assert.equal(admin.res.status, 403);
  assert.match(admin.text, /instrutor ou administração/);

  const catA = await grab(origin, ja, "/catalogo");
  await grab(origin, ja, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(catA.text) }),
  });
  const aula = await follow(origin, ja, "/aula/m01-aula");
  await grab(origin, ja, "/aula/m01-aula/nota", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(aula.text), body: "SEGredo-do-aluno-A-teste" }),
  });

  const catB = await grab(origin, jb, "/catalogo");
  await grab(origin, jb, "/matricular", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ csrf: csrfFrom(catB.text) }),
  });
  const cadernoB = await grab(origin, jb, "/caderno");
  assert.equal(cadernoB.text.includes("SEGRedo-do-aluno-A-teste"), false);

  const duvidaB = await grab(origin, jb, "/duvidas?aluno=1");
  assert.equal(duvidaB.res.status, 403);
});
