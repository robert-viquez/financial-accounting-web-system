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
import {
  createUnidadMedida,
  deleteUnidadMedida,
  getUnidadesMedida,
  updateUnidadMedida,
} from "@/modules/inventario/api/ProductosServices";

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
const inventario = reactive({
  lector_codigo_barras: true,
  prefijo_productos: "",
});
const unidades = ref([]);
const nuevaUnidad = reactive({
  codigo: "",
  nombre: "",
  simbolo: "",
  permite_decimales: true,
  estado: true,
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
    const [config, currentProfile, roleData, unitData] = await Promise.all([
      getConfiguracion(),
      getPerfil(),
      getRoles(),
      getUnidadesMedida({ ordering: "nombre" }),
    ]);
    Object.assign(empresa, config);
    impuestos.iva = Number(config.iva);
    impuestos.moneda = config.moneda;
    inventario.lector_codigo_barras = config.lector_codigo_barras;
    inventario.prefijo_productos = config.prefijo_productos;
    perfil.nombre = currentProfile.nombre;
    perfil.correo = currentProfile.correo;
    roles.value = roleData;
    unidades.value = unitData.results ?? unitData;
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
      updateConfiguracion({ ...empresa, ...impuestos, ...inventario }),
      updatePerfil({ first_name: perfil.nombre, correo: perfil.correo }),
    ]);
    mensaje("Configuración guardada correctamente.");
  } catch (error) {
    mensaje(error.response?.data?.detail || "No se pudo guardar la configuración.", "error");
  } finally {
    saving.value = false;
  }
}

async function agregarUnidad() {
  if (!nuevaUnidad.codigo || !nuevaUnidad.nombre || !nuevaUnidad.simbolo) {
    mensaje("Complete el código, nombre y símbolo de la unidad.", "error");
    return;
  }
  try {
    const unidad = await createUnidadMedida({
      ...nuevaUnidad,
      codigo: nuevaUnidad.codigo.trim().toUpperCase(),
    });
    unidades.value.push(unidad);
    Object.assign(nuevaUnidad, {
      codigo: "",
      nombre: "",
      simbolo: "",
      permite_decimales: true,
      estado: true,
    });
    mensaje("Unidad de medida agregada.");
  } catch (error) {
    mensaje(
      error.response?.data?.codigo?.[0] ||
        error.response?.data?.nombre?.[0] ||
        "No se pudo agregar la unidad.",
      "error"
    );
  }
}

async function guardarUnidad(unidad) {
  try {
    await updateUnidadMedida(unidad.id, unidad);
    mensaje(`Unidad ${unidad.nombre} actualizada.`);
  } catch {
    mensaje("No se pudo actualizar la unidad.", "error");
  }
}

async function eliminarUnidad(unidad) {
  try {
    await deleteUnidadMedida(unidad.id);
    unidades.value = unidades.value.filter((item) => item.id !== unidad.id);
    mensaje("Unidad eliminada.");
  } catch {
    mensaje(
      "No se puede eliminar una unidad que ya está asignada a productos. Puede desactivarla.",
      "error"
    );
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
        <v-card class="config-card">
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

      <v-col cols="12" lg="6">
        <v-card class="config-card">
          <v-card-title>Inventario y códigos</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="inventario.prefijo_productos"
                  label="Prefijo general de productos"
                  hint="Opcional. Ejemplo: QLS genera QLS-L-0001."
                  persistent-hint
                  maxlength="8"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
              <v-col cols="12">
                <v-switch
                  v-model="inventario.lector_codigo_barras"
                  label="Habilitar uso de lectores de código de barras"
                  color="primary"
                  hide-details
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12">
        <v-card class="config-card">
          <v-card-title>Unidades de medida</v-card-title>
          <v-card-subtitle>
            Configure gramos, kilogramos, unidades, paquetes u otras medidas del negocio.
          </v-card-subtitle>
          <v-card-text>
            <div class="units-list">
              <div
                v-for="unidad in unidades"
                :key="unidad.id"
                class="unit-row"
              >
                <v-text-field v-model="unidad.codigo" label="Código" variant="outlined" density="compact" hide-details />
                <v-text-field v-model="unidad.nombre" label="Nombre" variant="outlined" density="compact" hide-details />
                <v-text-field v-model="unidad.simbolo" label="Símbolo" variant="outlined" density="compact" hide-details />
                <v-checkbox v-model="unidad.permite_decimales" label="Decimales" hide-details />
                <v-switch v-model="unidad.estado" label="Activa" color="primary" hide-details />
                <div class="unit-actions">
                  <v-btn icon="mdi-content-save" variant="tonal" color="primary" size="small" @click="guardarUnidad(unidad)" />
                  <v-btn icon="mdi-delete" variant="text" color="error" size="small" @click="eliminarUnidad(unidad)" />
                </div>
              </div>

              <div class="unit-row unit-row--new">
                <v-text-field v-model="nuevaUnidad.codigo" label="Código nuevo" variant="outlined" density="compact" hide-details />
                <v-text-field v-model="nuevaUnidad.nombre" label="Nombre nuevo" variant="outlined" density="compact" hide-details />
                <v-text-field v-model="nuevaUnidad.simbolo" label="Símbolo" variant="outlined" density="compact" hide-details />
                <v-checkbox v-model="nuevaUnidad.permite_decimales" label="Decimales" hide-details />
                <v-switch v-model="nuevaUnidad.estado" label="Activa" color="primary" hide-details />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="agregarUnidad">Agregar</v-btn>
              </div>
            </div>
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

<style scoped>
.config-card {
  height: 100%;
  overflow: hidden;
}

.units-list {
  display: grid;
  gap: 12px;
}

.unit-row {
  align-items: center;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 10px;
  display: grid;
  gap: 10px;
  grid-template-columns: 100px minmax(180px, 1.5fr) minmax(100px, 0.7fr) 120px 100px auto;
  padding: 12px;
}

.unit-row--new {
  background: rgba(var(--v-theme-primary), 0.06);
  border-color: rgba(var(--v-theme-primary), 0.25);
}

.unit-actions {
  display: flex;
  gap: 4px;
}

@media (max-width: 1100px) {
  .unit-row {
    grid-template-columns: 100px 1fr 120px;
  }

  .unit-row > :nth-child(4),
  .unit-row > :nth-child(5),
  .unit-row > :nth-child(6) {
    justify-self: start;
  }
}

@media (max-width: 599px) {
  .unit-row {
    grid-template-columns: 1fr;
  }
}
</style>
