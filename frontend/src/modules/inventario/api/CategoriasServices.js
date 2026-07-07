import api from "@/api/axios";

export async function getCategorias(params = {}) {
  const response = await api.get("categorias-producto/", { params });
  return response.data;
}

export async function createCategoria(categoria) {
  const response = await api.post("categorias-producto/", categoria);
  return response.data;
}

export async function updateCategoria(id, categoria) {
  const response = await api.put(`categorias-producto/${id}/`, categoria);
  return response.data;
}

export async function deleteCategoria(id) {
  await api.delete(`categorias-producto/${id}/`);
}
