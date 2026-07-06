import api from "@/api/axios";

export async function getProveedores(params = {}) {
  const response = await api.get("proveedores/", { params });
  return response.data;
}

export async function createProveedor(proveedor) {
  const response = await api.post("proveedores/", proveedor);
  return response.data;
}

export async function updateProveedor(id, proveedor) {
  const response = await api.put(`proveedores/${id}/`, proveedor);
  return response.data;
}

export async function deleteProveedor(id) {
  await api.delete(`proveedores/${id}/`);
}