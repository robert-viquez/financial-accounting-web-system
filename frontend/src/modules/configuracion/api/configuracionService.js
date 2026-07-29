import api from "@/api/axios";

export async function getConfiguracion() {
  return (await api.get("configuracion-empresa/")).data;
}

export async function updateConfiguracion(data) {
  return (await api.patch("configuracion-empresa/", data)).data;
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

export async function getUsuarios() {
  return (await api.get("usuarios/")).data;
}

export async function getRoles() {
  return (await api.get("roles/")).data;
}

export async function getAuditoria() {
  return (await api.get("auditoria/", { params: { page_size: 20 } })).data;
}
