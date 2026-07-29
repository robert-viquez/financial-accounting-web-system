import api from "@/api/axios";

export async function getCuentasPorCobrar(params = {}) {
  const response = await api.get("cuentas-por-cobrar/", { params });
  return response.data;
}

export async function getPagosClientes(params = {}) {
  const response = await api.get("pagos-clientes/", { params });
  return response.data;
}

export async function createPagoCliente(pago) {
  const response = await api.post("pagos-clientes/", pago);
  return response.data;
}

export async function anularPagoCliente(id) {
  return (await api.post(`pagos-clientes/${id}/anular/`)).data;
}

export async function getCuentasPorPagar(params = {}) {
  const response = await api.get("cuentas-por-pagar/", { params });
  return response.data;
}

export async function getPagosProveedores(params = {}) {
  const response = await api.get("pagos-proveedores/", { params });
  return response.data;
}

export async function createPagoProveedor(pago) {
  const response = await api.post("pagos-proveedores/", pago);
  return response.data;
}

export async function anularPagoProveedor(id) {
  return (await api.post(`pagos-proveedores/${id}/anular/`)).data;
}
