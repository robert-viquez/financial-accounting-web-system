import api from "@/api/axios";

export async function getConfiguracion() {
  return (await api.get("configuracion-empresa/")).data;
}

export async function getIdentidadEmpresa() {
  return (await api.get("identidad-empresa/")).data;
}

export async function updateConfiguracion(data) {
  const options = data instanceof FormData
    ? { headers: { "Content-Type": undefined } }
    : undefined;
  return (await api.patch("configuracion-empresa/", data, options)).data;
}

export async function getPerfil() {
  return (await api.get("mi-perfil/")).data;
}

export async function updatePerfil(data) {
  return (await api.patch("mi-perfil/", data)).data;
}

export async function cambiarPassword(data) {
  return (await api.post("cambiar-password/", data)).data;
}

export async function getUsuarios(params = {}) {
  return (await api.get("usuarios/", { params })).data;
}

export async function createUsuario(data) {
  return (await api.post("usuarios/", data)).data;
}

export async function updateUsuario(id, data) {
  return (await api.patch(`usuarios/${id}/`, data)).data;
}

export async function deleteUsuario(id) {
  return api.delete(`usuarios/${id}/`);
}

export async function setUsuarioPassword(id, password) {
  return (await api.post(`usuarios/${id}/password/`, { password })).data;
}

export async function getRoles() {
  return (await api.get("roles/")).data;
}

export async function createRol(data) {
  return (await api.post("roles/", data)).data;
}

export async function updateRol(id, data) {
  return (await api.patch(`roles/${id}/`, data)).data;
}

export async function deleteRol(id) {
  return api.delete(`roles/${id}/`);
}

export async function getPermisos() {
  return (await api.get("permisos/")).data;
}

export async function getAuditoria(params = {}) {
  return (await api.get("auditoria/", { params: { page_size: 20, ...params } })).data;
}

export async function getInformacionSistema() {
  return (await api.get("informacion-sistema/")).data;
}
