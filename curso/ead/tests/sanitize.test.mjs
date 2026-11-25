import { test } from "node:test";
import assert from "node:assert/strict";
import { sanitizeHtml, safeHttpUrl } from "../src/sanitize.mjs";

test("remove script e handlers do markdown", () => {
  const dirty = `<p>ok</p><script>alert(1)</script><img src="/media/x.png" onerror="alert(1)"><a href="javascript:alert(1)">x</a>`;
  const clean = sanitizeHtml(dirty);
  assert.equal(clean.includes("script"), false);
  assert.equal(clean.includes("onerror"), false);
  assert.equal(clean.includes("javascript:"), false);
  assert.match(clean, /<p>ok<\/p>/);
});

test("recusa javascript, data e URL protocol-relative em href/src", () => {
  const dirty = `<a href="//evil.example/x">a</a><img src="https://evil.example/t.png"><img src="data:text/html,hi"><a href="javascript:alert(1)">j</a>`;
  const clean = sanitizeHtml(dirty);
  assert.equal(clean.includes("evil.example"), false);
  assert.equal(clean.includes("data:"), false);
  assert.equal(clean.includes("javascript:"), false);
});

test("URL http(s) só", () => {
  assert.equal(safeHttpUrl("https://example.com/a"), "https://example.com/a");
  assert.equal(safeHttpUrl("javascript:alert(1)"), "");
  assert.equal(safeHttpUrl("/interno"), "");
});
