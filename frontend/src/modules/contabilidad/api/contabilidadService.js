import api from "@/api/axios";

export async function getReporteContable(tipo, params = {}) {
  const response = await api.get(`reportes-contables/${tipo}/`, { params });
  return response.data;
}

export async function getCuentasContables(params = {}) {
  const response = await api.get("cuentas-contables/", { params });
  return response.data;
}

export async function getAsientos(params = {}) {
  const response = await api.get("asientos-contables/", { params });
  return response.data;
}

export async function getPeriodos(params = {}) {
  const response = await api.get("periodos-contables/", { params });
  return response.data;
}

export async function createAsiento(data) {
  return (await api.post("asientos-contables/", data)).data;
}

export async function contabilizarAsiento(id) {
  return (await api.post(`asientos-contables/${id}/contabilizar/`)).data;
}

export async function createCuenta(data) {
  return (await api.post("cuentas-contables/", data)).data;
}

export async function createPeriodo(data) {
  return (await api.post("periodos-contables/", data)).data;
}

export async function updatePeriodo(id, data) {
  return (await api.patch(`periodos-contables/${id}/`, data)).data;
}
