import api from "@/api/axios";

export async function getClientes(params = {}) {
  const response = await api.get("clientes/", { params });
  return response.data;
}

export async function createCliente(cliente) {
  const response = await api.post("clientes/", cliente);
  return response.data;
}

export async function updateCliente(id, cliente) {
  const response = await api.put(`clientes/${id}/`, cliente);
  return response.data;
}

export async function deleteCliente(id) {
  await api.delete(`clientes/${id}/`);
}