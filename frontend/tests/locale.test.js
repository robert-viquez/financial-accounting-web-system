import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

import { normalizeLocale, resolveLocale } from "../src/i18n/locale.js";

test("normalizes supported regional browser locales", () => {
  assert.equal(normalizeLocale("es-CR"), "es");
  assert.equal(normalizeLocale("es-MX"), "es");
  assert.equal(normalizeLocale("en-US"), "en");
  assert.equal(normalizeLocale("en-GB"), "en");
});

test("unsupported browser locales fall back to Spanish", () => {
  assert.equal(normalizeLocale("fr-FR"), "es");
  assert.equal(normalizeLocale(undefined), "es");
});

test("resolves user, application, browser, then Spanish", () => {
  assert.equal(resolveLocale({ userLocale: "en", defaultLocale: "es", browserLocale: "es-CR" }), "en");
  assert.equal(resolveLocale({ defaultLocale: "en", browserLocale: "es-CR" }), "en");
  assert.equal(resolveLocale({ defaultLocale: "auto", browserLocale: "en-GB" }), "en");
  assert.equal(resolveLocale({ defaultLocale: "auto", browserLocale: "de-DE" }), "es");
});

function leafKeys(value, prefix = "") {
  return Object.entries(value).flatMap(([key, child]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    return child && typeof child === "object" ? leafKeys(child, path) : [path];
  });
}

test("Spanish and English dictionaries have identical keys", async () => {
  const base = new URL("../src/i18n/locales/", import.meta.url);
  const [es, en] = await Promise.all([
    readFile(new URL("es.json", base), "utf8").then(JSON.parse),
    readFile(new URL("en.json", base), "utf8").then(JSON.parse),
  ]);
  assert.deepEqual(leafKeys(en).sort(), leafKeys(es).sort());
});
