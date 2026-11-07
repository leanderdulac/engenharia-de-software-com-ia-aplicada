#!/usr/bin/env node
import { mkdirSync } from "node:fs";
import { dbFile, dataDir } from "./config.mjs";
import { openDb } from "./db.mjs";
import { createAdmin, seedCatalogIndex, seedDemo } from "./seed.mjs";

const cmd = process.argv[2] || "help";

function db() {
  mkdirSync(dataDir(), { recursive: true });
  return openDb(dbFile());
}

if (cmd === "migrate") {
  const database = db();
  seedCatalogIndex(database);
  console.log("schema + índice FTS em", dbFile());
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
} else if (cmd === "seed") {
  if (process.env.EAD_SEED_DEMO !== "1") {
    console.error("Recuse seed acidental: exporte EAD_SEED_DEMO=1 e as senhas EAD_DEMO_*_PASSWORD.");
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
  EAD_ADMIN_EMAIL=… EAD_ADMIN_PASSWORD=… node src/cli.mjs create-admin
  EAD_SEED_DEMO=1 EAD_DEMO_INSTRUCTOR_PASSWORD=… EAD_DEMO_ALUNO_A_PASSWORD=… EAD_DEMO_ALUNO_B_PASSWORD=… node src/cli.mjs seed`);
}
