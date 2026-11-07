import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { boot } from "../src/server.mjs";

const password = "Admin-Probe-teste-10";
const { app, db } = boot({
  dbPath: path.join(mkdtempSync(path.join(tmpdir(), "ead-signup-")), "ead.sqlite"),
  createAdminOpts: { email: "admin.probe@local.test", password, name: "Probe" },
});
const server = await new Promise((resolve) => {
  const httpd = app.listen(0, "127.0.0.1", () => resolve(httpd));
});
const origin = `http://127.0.0.1:${server.address().port}`;

function snap() {
  return {
    users: db.prepare("SELECT COUNT(*) AS n FROM users").get().n,
    attempts: db.prepare("SELECT COUNT(*) AS n FROM login_attempts").get().n,
    rows: db.prepare("SELECT email, role FROM users ORDER BY id").all(),
  };
}

async function exchange(jar, url, opts = {}) {
  const res = await fetch(origin + url, {
    ...opts,
    redirect: "manual",
    headers: { ...(opts.headers || {}), cookie: jar.cookie || "" },
  });
  const set = typeof res.headers.getSetCookie === "function" ? res.headers.getSetCookie() : [];
  for (const c of set) {
    const nv = c.split(";")[0];
    jar.cookie = jar.cookie ? `${jar.cookie}; ${nv}` : nv;
  }
  return { status: res.status, text: await res.text(), location: res.headers.get("location") };
}

const before = snap();
const jar = {};
const get = await exchange(jar, "/registar");
const entrar = await exchange(jar, "/entrar");
const csrf = (entrar.text.match(/name="csrf"\s+value="([^"]+)"/) || [])[1] || "";
const body = new URLSearchParams({
  name: "Intruso",
  email: "intruso.signup@local.test",
  password: "Intruso-teste-10",
  csrf,
});
const post = await exchange(jar, "/registar", {
  method: "POST",
  headers: { "content-type": "application/x-www-form-urlencoded" },
  body,
});
const api = await exchange(jar, "/api/registar", {
  method: "POST",
  headers: { "content-type": "application/x-www-form-urlencoded" },
  body,
});
const json = await exchange(jar, "/registar", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    name: "Intruso",
    email: "intruso.json@local.test",
    password: "Intruso-teste-10",
    csrf,
  }),
});
const login = await exchange(jar, "/entrar", {
  method: "POST",
  headers: { "content-type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({
    email: "admin.probe@local.test",
    password,
    csrf,
    next: "/dashboard",
  }),
});
const dash = login.status === 303 ? await exchange(jar, login.location || "/dashboard") : { status: 0, text: "" };
const after = snap();
console.log(
  JSON.stringify({
    flag: process.env.EAD_OPEN_SIGNUP ?? null,
    nodeEnv: process.env.NODE_ENV ?? null,
    csrfLen: csrf.length,
    getStatus: get.status,
    getForm: get.text.includes("<form") && get.text.includes('action="/registar"'),
    getPassword: get.text.includes('name="password"'),
    getEmail: get.text.includes('name="email"'),
    getName: get.text.includes('name="name"'),
    postStatus: post.status,
    apiStatus: api.status,
    jsonStatus: json.status,
    loginStatus: login.status,
    dashOk: dash.status === 200 && dash.text.includes("Painel"),
    before,
    after,
  })
);
server.close();
db.close();
