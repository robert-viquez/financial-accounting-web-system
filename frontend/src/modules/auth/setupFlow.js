export function resolveSetupNavigation({ setupRequired, path, authenticated }) {
  if (setupRequired && path !== "/setup") return "/setup";
  if (!setupRequired && path === "/setup") return authenticated ? "/dashboard" : "/login";
  return undefined;
}
