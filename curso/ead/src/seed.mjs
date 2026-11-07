import { hashPassword, validEmail, validPassword } from "./auth.mjs";
import { indexContent, loadCatalog } from "./catalog.mjs";
import { nowIso } from "./db.mjs";

function upsertUser(db, { email, password, name, role, demo }) {
  const existing = db.prepare("SELECT id FROM users WHERE email = ?").get(email);
  const hash = hashPassword(password);
  if (existing) {
    db.prepare("UPDATE users SET password_hash = ?, name = ?, role = ?, demo = ? WHERE id = ?").run(
      hash,
      name,
      role,
      demo ? 1 : 0,
      existing.id
    );
    return existing.id;
  }
  const info = db
    .prepare(
      "INSERT INTO users (email, password_hash, name, role, demo, diagnostic_done, created_at) VALUES (?, ?, ?, ?, ?, 0, ?)"
    )
    .run(email, hash, name, role, demo ? 1 : 0, nowIso());
  return Number(info.lastInsertRowid);
}

export function seedCatalogIndex(db) {
  const catalog = loadCatalog();
  indexContent(db, catalog);
  return catalog;
}

export function createAdmin(db, { email, password, name }) {
  const e = String(email || "").trim().toLowerCase();
  if (!validEmail(e)) throw new Error("E-mail inválido.");
  if (!validPassword(password)) throw new Error("Senha: 10 a 128 caracteres.");
  return upsertUser(db, {
    email: e,
    password,
    name: name || "Administração local",
    role: "admin",
    demo: false,
  });
}

/**
 * Fixtures visuais DEMONSTRAÇÃO/TESTE. Não são alunos reais.
 * Senhas só via env / argumentos — nunca gravadas no Git.
 */
export function seedDemo(db, passwords) {
  const need = ["instructor", "alunoA", "alunoB"];
  for (const k of need) {
    if (!validPassword(passwords[k])) {
      throw new Error(`Senha de seed em falta ou curta (${k}). Defina EAD_DEMO_*_PASSWORD.`);
    }
  }
  const instructorId = upsertUser(db, {
    email: "instrutor.demo@local.test",
    password: passwords.instructor,
    name: "DEMONSTRAÇÃO/TESTE — Instrutor",
    role: "instrutor",
    demo: true,
  });
  const a = upsertUser(db, {
    email: "aluno-a.demo@local.test",
    password: passwords.alunoA,
    name: "DEMONSTRAÇÃO/TESTE — Aluno A",
    role: "aluno",
    demo: true,
  });
  const b = upsertUser(db, {
    email: "aluno-b.demo@local.test",
    password: passwords.alunoB,
    name: "DEMONSTRAÇÃO/TESTE — Aluno B",
    role: "aluno",
    demo: true,
  });
  return { instructorId, alunoA: a, alunoB: b };
}
