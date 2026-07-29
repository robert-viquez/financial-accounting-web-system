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

export async function getProductoPorCodigo(codigo) {
  const response = await api.get("productos/por-codigo-barras/", {
    params: { codigo },
  });
  return response.data;
}

export async function registrarEntradaPorCodigo(data) {
  const response = await api.post("productos/registrar-entrada/", data);
  return response.data;
}

export async function getUnidadesMedida(params = {}) {
  const response = await api.get("unidades-medida/", { params });
  return response.data;
}

export async function createUnidadMedida(data) {
  return (await api.post("unidades-medida/", data)).data;
}

export async function updateUnidadMedida(id, data) {
  return (await api.patch(`unidades-medida/${id}/`, data)).data;
}

export async function deleteUnidadMedida(id) {
  await api.delete(`unidades-medida/${id}/`);
}
