import api from "@/api/axios";

export async function getVentas(params = {}) {
  const response = await api.get("ventas/", { params });
  return response.data;
}

export async function getVenta(id) {
  const response = await api.get(`ventas/${id}/`);
  return response.data;
}

export async function createVenta(venta) {
  const response = await api.post("ventas/", venta);
  return response.data;
}

export async function updateVenta(id, venta) {
  const response = await api.put(`ventas/${id}/`, venta);
  return response.data;
}

export async function deleteVenta(id) {
  await api.delete(`ventas/${id}/`);
}

export async function getTiposVenta(params = {}) {
  const response = await api.get("tipos-venta/", { params });
  return response.data;
}

export async function createTipoVenta(data) {
  const response = await api.post("tipos-venta/", data);
  return response.data;
}

export async function updateTipoVenta(id, data) {
  const response = await api.put(`tipos-venta/${id}/`, data);
  return response.data;
}

export async function deleteTipoVenta(id) {
  await api.delete(`tipos-venta/${id}/`);
}
