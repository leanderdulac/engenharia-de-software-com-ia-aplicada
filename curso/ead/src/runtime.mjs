/**
 * Modo produção = uma instalação privada desta pós (um processo, um SQLite em disco).
 * Não é cluster, nem Pages, nem publicação do material CC BY-NC-ND.
 */

export function isProduction(env = process.env) {
  return env.NODE_ENV === "production";
}

/**
 * Auto-registo HTTP (GET e POST /registar).
 * Precedência, a mesma com NODE_ENV=production, development ou ausente:
 *   EAD_OPEN_SIGNUP=1     abre (único opt-in)
 *   EAD_OPEN_SIGNUP=0     fecha
 *   ausente, vazio ou outro valor  fecha
 * NODE_ENV não reabre o formulário. create-admin, create-user e o seed
 * de demonstração não passam por aqui.
 */
export function signupOpen(env = process.env) {
  return env.EAD_OPEN_SIGNUP === "1";
}

export function trustProxy(env = process.env) {
  return env.EAD_TRUST_PROXY === "1";
}

/**
 * Falha o arranque se a instalação diz ser produção e a config deixaria
 * cookies em claro, seed de demonstração ou base no disco efémero por omissão.
 */
export function assertBootConfig(env = process.env) {
  if (!isProduction(env)) return [];
  const problems = [];
  if (env.EAD_SECURE_COOKIES !== "1") {
    problems.push("EAD_SECURE_COOKIES=1 (HTTPS na borda; o processo fala HTTP)");
  }
  if (!String(env.EAD_DATA_DIR || "").trim()) {
    problems.push("EAD_DATA_DIR apontando para disco persistente");
  }
  if (env.EAD_SEED_DEMO === "1") {
    problems.push("EAD_SEED_DEMO é proibido com NODE_ENV=production");
  }
  if (problems.length) {
    const err = new Error(`Configuração de produção recusada: ${problems.join("; ")}.`);
    err.code = "EAD_CONFIG";
    throw err;
  }
  return ["secure-cookies", "data-dir", "sem-seed-demo"];
}
