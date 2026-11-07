#!/usr/bin/env node
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { backup } from "node:sqlite";
import { dbFile, dataDir } from "./config.mjs";
import { openDb } from "./db.mjs";
import { schemaVersion } from "./migrate.mjs";
import { integrityOk, issueReset } from "./ops.mjs";
import { assertBootConfig } from "./runtime.mjs";
import { createAdmin, seedCatalogIndex, seedDemo } from "./seed.mjs";
import { validEmail, validPassword } from "./auth.mjs";
import { hashPassword } from "./auth.mjs";
import { nowIso } from "./db.mjs";

const cmd = process.argv[2] || "help";

function db() {
  mkdirSync(dataDir(), { recursive: true });
  return openDb(dbFile());
}

if (cmd === "migrate") {
  if (process.env.NODE_ENV === "production") assertBootConfig();
  const database = db();
  seedCatalogIndex(database);
  console.log("schema", schemaVersion(database), "em", dbFile());
} else if (cmd === "check") {
  const database = db();
  const ok = integrityOk(database);
  console.log(JSON.stringify({ file: dbFile(), schema: schemaVersion(database), integrity: ok ? "ok" : "falha" }));
  if (!ok) process.exit(1);
} else if (cmd === "backup") {
  const dest = process.argv[3];
  if (!dest) {
    console.error("Uso: node src/cli.mjs backup <ficheiro.sqlite>");
    process.exit(1);
  }
  const database = db();
  database.exec("PRAGMA wal_checkpoint(PASSIVE);");
  const abs = path.resolve(dest);
  await backup(database, abs, { rate: 100 });
  console.log("backup", abs);
} else if (cmd === "restore") {
  const src = process.argv[3];
  if (!src || !existsSync(path.resolve(src))) {
    console.error("Ficheiro de backup inexistente. Restore recusado (a base actual não foi alterada).");
    process.exit(1);
  }
  const probe = openDb(path.resolve(src));
  const ok = integrityOk(probe);
  const version = schemaVersion(probe);
  probe.close();
  if (!ok) {
    console.error("Backup sem integridade. Restore recusado.");
    process.exit(1);
  }
  mkdirSync(dataDir(), { recursive: true });
  copyFileSync(path.resolve(src), dbFile());
  console.log("restaurado", dbFile(), "schema", version);
} else if (cmd === "create-admin") {
  const email = process.env.EAD_ADMIN_EMAIL;
  const password = process.env.EAD_ADMIN_PASSWORD;
  const name = process.env.EAD_ADMIN_NAME || "Administração local";
  if (!email || !password) {
    console.error("Defina EAD_ADMIN_EMAIL e EAD_ADMIN_PASSWORD no ambiente. Não os cole em ficheiros versionados.");
    process.exit(1);
  }
  const database = db();
  seedCatalogIndex(database);
  const id = createAdmin(database, { email, password, name });
  console.log("admin id=", id, "email=", email.toLowerCase());
} else if (cmd === "create-user") {
  const email = String(process.env.EAD_USER_EMAIL || "").trim().toLowerCase();
  const password = process.env.EAD_USER_PASSWORD || "";
  const name = String(process.env.EAD_USER_NAME || "").trim().slice(0, 80);
  const role = process.env.EAD_USER_ROLE || "aluno";
  if (!validEmail(email) || !validPassword(password) || !name) {
    console.error("EAD_USER_EMAIL, EAD_USER_NAME e EAD_USER_PASSWORD (10–128) são obrigatórios.");
    process.exit(1);
  }
  if (!["aluno", "instrutor"].includes(role)) {
    console.error("EAD_USER_ROLE: aluno ou instrutor. Admin continua em create-admin.");
    process.exit(1);
  }
  const database = db();
  const info = database
    .prepare(
      "INSERT INTO users (email, password_hash, name, role, demo, diagnostic_done, disabled, created_at) VALUES (?, ?, ?, ?, 0, 0, 0, ?)"
    )
    .run(email, hashPassword(password), name, role, nowIso());
  console.log("user id=", Number(info.lastInsertRowid), "role=", role);
} else if (cmd === "reset-token") {
  const email = String(process.env.EAD_RESET_EMAIL || "").trim().toLowerCase();
  const database = db();
  const user = database.prepare("SELECT id, role FROM users WHERE email = ?").get(email);
  if (!user) {
    console.error("Conta inexistente.");
    process.exit(1);
  }
  const token = issueReset(database, user.id);
  console.log("token_uso_unico", token);
  console.log("expira_em_minutos 30. Não envie isto para o Git nem para um canal público.");
} else if (cmd === "seed") {
  if (process.env.NODE_ENV === "production" || process.env.EAD_SEED_DEMO !== "1") {
    console.error("Seed recusado. Fora de produção: EAD_SEED_DEMO=1 e senhas EAD_DEMO_*_PASSWORD. Em NODE_ENV=production o seed não corre.");
    process.exit(1);
  }
  const database = db();
  seedCatalogIndex(database);
  seedDemo(database, {
    instructor: process.env.EAD_DEMO_INSTRUCTOR_PASSWORD,
    alunoA: process.env.EAD_DEMO_ALUNO_A_PASSWORD,
    alunoB: process.env.EAD_DEMO_ALUNO_B_PASSWORD,
  });
  console.log("Seed DEMONSTRAÇÃO/TESTE: instrutor.demo@local.test, aluno-a.demo@local.test, aluno-b.demo@local.test");
} else {
  console.log(`comandos:
  node src/cli.mjs migrate
  node src/cli.mjs check
  node src/cli.mjs backup ./data/ead-backup.sqlite
  node src/cli.mjs restore ./data/ead-backup.sqlite
  EAD_ADMIN_EMAIL=… EAD_ADMIN_PASSWORD=… node src/cli.mjs create-admin
  EAD_USER_EMAIL=… EAD_USER_NAME=… EAD_USER_PASSWORD=… EAD_USER_ROLE=aluno node src/cli.mjs create-user
  EAD_RESET_EMAIL=… node src/cli.mjs reset-token
  EAD_SEED_DEMO=1 … node src/cli.mjs seed   (recusado em produção)`);
}
