import api from "@/api/axios";

export async function getCompras(params = {}) {
  const response = await api.get("compras/", { params });
  return response.data;
}

export async function createCompra(compra) {
  const response = await api.post("compras/", compra);
  return response.data;
}

export async function deleteCompra(id) {
  await api.delete(`compras/${id}/`);
}