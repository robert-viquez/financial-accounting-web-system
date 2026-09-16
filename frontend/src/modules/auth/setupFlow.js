export function resolveSetupNavigation({ setupRequired, path, authenticated, demoMode = false }) {
  if (demoMode) return path === "/setup" ? (authenticated ? "/dashboard" : "/login") : undefined;
  if (setupRequired && path !== "/setup") return "/setup";
  if (!setupRequired && path === "/setup") return authenticated ? "/dashboard" : "/login";
  return undefined;
}
