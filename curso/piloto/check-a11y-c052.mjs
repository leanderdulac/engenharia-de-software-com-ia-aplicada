#!/usr/bin/env node
/**
 * Checagem estática C05.2 (Pix templates). Não é auditoria WCAG nem certificação.
 * Não sobe o Angular. Não valida contraste computado nem leitores de ecrã.
 *
 *   node curso/piloto/check-a11y-c052.mjs
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const REPO = join(dirname(fileURLToPath(import.meta.url)), "../..");
const PIX = join(REPO, "modulo05-ferramentas-de-IA-para-UI-UX/modulo-02/pix-app/src");
const FAIL = [];

function read(rel) {
  return readFileSync(join(PIX, rel), "utf8");
}

const index = read("index.html");
if (!/lang="pt-BR"/.test(index)) FAIL.push("index.html: lang deve ser pt-BR (UI em português)");

const app = read("app/app.html");
if (!/Pular para o conteúdo/.test(app)) FAIL.push("app.html: falta skip-link");
if (!/aria-label="Principal"/.test(app)) FAIL.push("app.html: nav sem aria-label");
if (!/id="conteudo"/.test(app)) FAIL.push("app.html: main sem id=conteudo");

const transfer = read("app/pix-transfer/pix-transfer.html");
if (!/label for="pixKey"/.test(transfer)) FAIL.push("pix-transfer: falta label da chave");
if (!/label for="transferAmount"/.test(transfer)) FAIL.push("pix-transfer: falta label do valor");
if (!/id="pix-transfer-title"/.test(transfer)) FAIL.push("pix-transfer: form sem título associado");

const modalHtml = read("app/components/error-modal/error-modal.html");
const modalTs = read("app/components/error-modal/error-modal.ts");
if (!/role="alertdialog"/.test(modalHtml)) FAIL.push("error-modal: falta role=alertdialog");
if (!/aria-modal="true"/.test(modalHtml)) FAIL.push("error-modal: falta aria-modal");
if (!/keydown\.escape/.test(modalTs)) FAIL.push("error-modal.ts: falta handler Escape");

const history = read("app/pix-history/pix-history.component.html");
if (!/role="list"/.test(history)) FAIL.push("pix-history: lista sem role=list");
if (!/aria-hidden="true"/.test(history)) FAIL.push("pix-history: ícone decorativo sem aria-hidden");

const receipt = read("app/pix-receipt/pix-receipt.html");
if (!/aria-hidden="true"/.test(receipt)) FAIL.push("pix-receipt: ícones decorativos sem aria-hidden");

if (FAIL.length) {
  for (const f of FAIL) console.error(`FAIL  ${f}`);
  process.exit(1);
}
console.log("OK    C05.2 estático (Pix templates): lang, skip-link, labels, modal Escape, ícones");
console.log("Isto não certifica WCAG nem aprendizagem. CFP não foi compilado aqui.");
