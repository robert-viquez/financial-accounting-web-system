<script setup>
import { onMounted, reactive, ref } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import {
  cambiarPassword as cambiarPasswordApi,
  getConfiguracion,
  getAuditoria,
  getPerfil,
  getRoles,
  getUsuarios,
  updateConfiguracion,
  updatePerfil,
} from "@/modules/configuracion/api/configuracionService";

const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");
const saving = ref(false);

const empresa = reactive({
  nombre: "",
  identificacion: "",
  telefono: "",
  correo: "",
  direccion: "",
});

const impuestos = reactive({
  iva: 13,
  moneda: "CRC",
});

const perfil = reactive({
  nombre: "",
  correo: "",
});

const password = reactive({
  actual: "",
  nueva: "",
  confirmar: "",
});

const roles = ref([]);
const usuarios = ref([]);
const auditoria = ref([]);

function mensaje(texto, color = "success") {
  snackbarText.value = texto;
  snackbarColor.value = color;
  snackbar.value = true;
}

async function cargarConfiguracion() {
  try {
    const [config, currentProfile, roleData] = await Promise.all([
      getConfiguracion(),
      getPerfil(),
      getRoles(),
    ]);
    Object.assign(empresa, config);
    impuestos.iva = Number(config.iva);
    impuestos.moneda = config.moneda;
    perfil.nombre = currentProfile.nombre;
    perfil.correo = currentProfile.correo;
    roles.value = roleData;
    try {
      const userData = await getUsuarios();
      usuarios.value = userData.results ?? userData;
      const auditData = await getAuditoria();
      auditoria.value = auditData.results ?? auditData;
    } catch {
      usuarios.value = [currentProfile];
    }
  } catch {
    mensaje("No se pudo cargar la configuración.", "error");
  }
}

async function guardarConfiguracion() {
  saving.value = true;
  try {
    await Promise.all([
      updateConfiguracion({ ...empresa, ...impuestos }),
      updatePerfil({ first_name: perfil.nombre, correo: perfil.correo }),
    ]);
    mensaje("Configuración guardada correctamente.");
  } catch (error) {
    mensaje(error.response?.data?.detail || "No se pudo guardar la configuración.", "error");
  } finally {
    saving.value = false;
  }
}

async function cambiarPassword() {
  if (!password.actual || !password.nueva || password.nueva !== password.confirmar) {
    mensaje("Revise la contraseña actual y la confirmación.", "error");
    return;
  }
  try {
    await cambiarPasswordApi({ actual: password.actual, nueva: password.nueva });
    password.actual = "";
    password.nueva = "";
    password.confirmar = "";
    mensaje("Contraseña actualizada correctamente.");
  } catch (error) {
    const data = error.response?.data;
    mensaje(data?.actual?.[0] || data?.nueva?.[0] || "No se pudo cambiar la contraseña.", "error");
  }
}

onMounted(cargarConfiguracion);
</script>

<template>
  <section>
    <PageHeader
      title="Configuración"
      subtitle="Parámetros generales, impuestos, usuarios, roles y perfil."
    />

    <v-row>
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Datos de la empresa</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="empresa.nombre" label="Nombre" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="empresa.identificacion" label="Identificación" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="empresa.telefono" label="Teléfono" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="empresa.correo" label="Correo" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="empresa.direccion" label="Dirección" variant="outlined" density="compact" rows="2" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12">
        <v-card>
          <v-card-title>Auditoría reciente</v-card-title>
          <v-table density="compact">
            <thead><tr><th>Fecha</th><th>Usuario</th><th>Acción</th><th>Ruta</th><th>Resultado</th></tr></thead>
            <tbody>
              <tr v-for="item in auditoria" :key="item.id">
                <td>{{ new Date(item.fecha).toLocaleString("es-CR") }}</td>
                <td>{{ item.usuario_nombre }}</td>
                <td>{{ item.metodo }}</td>
                <td>{{ item.ruta }}</td>
                <td>{{ item.codigo_respuesta }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Impuestos</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model.number="impuestos.iva" label="IVA (%)" type="number" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="impuestos.moneda"
                  :items="['CRC', 'USD']"
                  label="Moneda"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Perfil</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="perfil.nombre" label="Nombre" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="perfil.correo" label="Correo" variant="outlined" density="compact" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Cambiar contraseña</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="4">
                <v-text-field v-model="password.actual" label="Actual" type="password" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12" sm="4">
                <v-text-field v-model="password.nueva" label="Nueva" type="password" variant="outlined" density="compact" />
              </v-col>
              <v-col cols="12" sm="4">
                <v-text-field v-model="password.confirmar" label="Confirmar" type="password" variant="outlined" density="compact" />
              </v-col>
            </v-row>
            <v-btn color="primary" variant="tonal" @click="cambiarPassword">
              Cambiar contraseña
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Usuarios</v-card-title>
          <v-table density="compact">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Rol</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="usuario in usuarios" :key="usuario.nombre">
                <td>{{ usuario.nombre }}</td>
                <td>{{ usuario.roles?.join(", ") || "Sin rol" }}</td>
                <td>{{ usuario.is_active ? "Activo" : "Inactivo" }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Roles</v-card-title>
          <v-list density="compact">
            <v-list-item
              v-for="rol in roles"
              :key="rol.nombre"
              :title="rol.nombre"
              :subtitle="rol.descripcion"
            />
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <div class="d-flex justify-end mt-4">
      <v-btn color="primary" prepend-icon="mdi-content-save" :loading="saving" @click="guardarConfiguracion">
        Guardar configuración
      </v-btn>
    </div>

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>
