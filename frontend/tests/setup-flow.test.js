import test from "node:test";
import assert from "node:assert/strict";

import { resolveSetupNavigation } from "../src/modules/auth/setupFlow.js";

test("fresh installations are routed to setup", () => {
  assert.equal(
    resolveSetupNavigation({ setupRequired: true, path: "/login", authenticated: false }),
    "/setup",
  );
  assert.equal(
    resolveSetupNavigation({ setupRequired: true, path: "/setup", authenticated: false }),
    undefined,
  );
});

test("initialized installations cannot open setup", () => {
  assert.equal(
    resolveSetupNavigation({ setupRequired: false, path: "/setup", authenticated: false }),
    "/login",
  );
  assert.equal(
    resolveSetupNavigation({ setupRequired: false, path: "/setup", authenticated: true }),
    "/dashboard",
  );
});
