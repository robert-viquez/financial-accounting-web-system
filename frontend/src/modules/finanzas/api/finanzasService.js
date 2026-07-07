import api from "@/api/axios";

export async function getCuentasPorCobrar(params = {}) {
  const response = await api.get("cuentas-por-cobrar/", { params });
  return response.data;
}

export async function updateCuentaPorCobrar(id, cuenta) {
  const response = await api.put(`cuentas-por-cobrar/${id}/`, cuenta);
  return response.data;
}

export async function deleteCuentaPorCobrar(id) {
  await api.delete(`cuentas-por-cobrar/${id}/`);
}

export async function getPagosClientes(params = {}) {
  const response = await api.get("pagos-clientes/", { params });
  return response.data;
}

export async function createPagoCliente(pago) {
  const response = await api.post("pagos-clientes/", pago);
  return response.data;
}

export async function getCuentasPorPagar(params = {}) {
  const response = await api.get("cuentas-por-pagar/", { params });
  return response.data;
}

export async function updateCuentaPorPagar(id, cuenta) {
  const response = await api.put(`cuentas-por-pagar/${id}/`, cuenta);
  return response.data;
}

export async function deleteCuentaPorPagar(id) {
  await api.delete(`cuentas-por-pagar/${id}/`);
}

export async function getPagosProveedores(params = {}) {
  const response = await api.get("pagos-proveedores/", { params });
  return response.data;
}

export async function createPagoProveedor(pago) {
  const response = await api.post("pagos-proveedores/", pago);
  return response.data;
}
