import api from "@/api/axios";

export async function getMediosPago(params = {}) {
  const response = await api.get("medios-pago/", { params });
  return response.data;
}