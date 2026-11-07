import { SCHEMA } from "./schema.mjs";

function addColumn(db, table, column, ddl) {
  const cols = db.prepare(`PRAGMA table_info(${table})`).all();
  if (cols.some((c) => c.name === column)) return;
  db.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${ddl}`);
}

const MIGRATIONS = [
  {
    id: 1,
    name: "base",
    up(db) {
      db.exec(SCHEMA);
    },
  },
  {
    id: 2,
    name: "operacao",
    up(db) {
      addColumn(db, "users", "disabled", "INTEGER NOT NULL DEFAULT 0");
      addColumn(db, "users", "password_changed_at", "TEXT");
      db.exec(`
        CREATE TABLE IF NOT EXISTS audit_log (
          id INTEGER PRIMARY KEY,
          actor_id INTEGER,
          action TEXT NOT NULL,
          target TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS password_resets (
          id INTEGER PRIMARY KEY,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          token_hash TEXT NOT NULL UNIQUE,
          expires_at INTEGER NOT NULL,
          used_at TEXT,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
      `);
    },
  },
];

export const SCHEMA_VERSION = MIGRATIONS[MIGRATIONS.length - 1].id;

export function migrate(db) {
  db.exec(`CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
  )`);
  const applied = new Set(db.prepare("SELECT id FROM schema_migrations").all().map((r) => r.id));
  const insert = db.prepare("INSERT INTO schema_migrations (id, name, applied_at) VALUES (?, ?, ?)");
  for (const step of MIGRATIONS) {
    if (applied.has(step.id)) continue;
    db.exec("BEGIN");
    try {
      step.up(db);
      insert.run(step.id, step.name, new Date().toISOString());
      db.exec("COMMIT");
    } catch (err) {
      db.exec("ROLLBACK");
      throw err;
    }
  }
  return SCHEMA_VERSION;
}

export function schemaVersion(db) {
  const row = db.prepare("SELECT MAX(id) AS v FROM schema_migrations").get();
  return row?.v || 0;
}
