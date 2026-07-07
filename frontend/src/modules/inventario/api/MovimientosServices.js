import api from "@/api/axios";

export async function getMovimientos(params = {}) {
  const response = await api.get("movimientos-inventario/", { params });
  return response.data;
}
