import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const cli = fileURLToPath(new URL("../src/cli.mjs", import.meta.url));

describe("restore não inventa uma base vazia", () => {
  it("recusa caminho em falta e deixa o sqlite existente", () => {
    const dir = mkdtempSync(path.join(tmpdir(), "ead-restore-"));
    const db = path.join(dir, "ead.sqlite");
    writeFileSync(db, "nao-apagar");
    const missing = path.join(dir, "nao-existe.sqlite");
    const run = spawnSync(process.execPath, [cli, "restore", missing], {
      encoding: "utf8",
      env: { ...process.env, EAD_DATA_DIR: dir },
    });
    assert.notEqual(run.status, 0);
    assert.match(run.stderr, /inexistente/);
    assert.equal(readFileSync(db, "utf8"), "nao-apagar");
  });
});
