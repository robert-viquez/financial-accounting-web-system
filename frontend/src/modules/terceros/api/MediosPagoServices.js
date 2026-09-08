import api from "@/api/axios";

export async function getMediosPago(params = {}) {
  const response = await api.get("medios-pago/", { params });
  return response.data;
}

export async function createMedioPago(data) {
  const response = await api.post("medios-pago/", data);
  return response.data;
}

export async function updateMedioPago(id, data) {
  const response = await api.put(`medios-pago/${id}/`, data);
  return response.data;
}

export async function deleteMedioPago(id) {
  await api.delete(`medios-pago/${id}/`);
}
