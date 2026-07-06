import api from "@/api/axios";

export async function getProductos(params = {}) {
  const response = await api.get("productos/", { params });
  return response.data;
}

export async function createProducto(producto) {
  const response = await api.post("productos/", producto);
  return response.data;
}

export async function updateProducto(id, producto) {
  const response = await api.put(`productos/${id}/`, producto);
  return response.data;
}

export async function deleteProducto(id) {
  await api.delete(`productos/${id}/`);
}