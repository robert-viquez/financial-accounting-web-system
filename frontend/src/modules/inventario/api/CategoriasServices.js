import api from "@/api/axios";

export async function getCategorias() {
  const response = await api.get("categorias-producto/");
  return response.data.results || response.data;
}