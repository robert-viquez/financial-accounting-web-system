import api from "@/api/axios";

let setupRequiredPromise;

export function getSetupRequired({ refresh = false } = {}) {
  if (refresh || !setupRequiredPromise) {
    setupRequiredPromise = api
      .get("setup/status/")
      .then((response) => response.data.setup_required === true)
      .catch((error) => {
        setupRequiredPromise = undefined;
        throw error;
      });
  }
  return setupRequiredPromise;
}

export async function createInitialAdmin(payload) {
  const response = await api.post("setup/admin/", payload);
  setupRequiredPromise = Promise.resolve(false);
  return response.data;
}
