<script setup>
import { onMounted, reactive, ref } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";

const snackbar = ref(false);
const snackbarText = ref("");

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

const roles = [
  { nombre: "Administrador", descripcion: "Acceso completo al sistema." },
  { nombre: "Contabilidad", descripcion: "Gestión contable y reportes." },
  { nombre: "Operaciones", descripcion: "Ventas, compras e inventario." },
];

const usuarios = [
  { nombre: "Usuario actual", rol: "Administrador", estado: "Activo" },
];

function cargarConfiguracion() {
  const saved = JSON.parse(localStorage.getItem("app_configuracion") || "{}");
  Object.assign(empresa, saved.empresa || {});
  Object.assign(impuestos, saved.impuestos || {});
  Object.assign(perfil, saved.perfil || {});
}

function guardarConfiguracion() {
  localStorage.setItem(
    "app_configuracion",
    JSON.stringify({
      empresa,
      impuestos,
      perfil,
    })
  );

  snackbarText.value = "Configuración guardada correctamente.";
  snackbar.value = true;
}

function cambiarPassword() {
  if (!password.actual || !password.nueva || password.nueva !== password.confirmar) {
    snackbarText.value = "Revise la contraseña actual y la confirmación.";
    snackbar.value = true;
    return;
  }

  password.actual = "";
  password.nueva = "";
  password.confirmar = "";
  snackbarText.value = "Solicitud de cambio de contraseña registrada.";
  snackbar.value = true;
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
                <td>{{ usuario.rol }}</td>
                <td>{{ usuario.estado }}</td>
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
      <v-btn color="primary" prepend-icon="mdi-content-save" @click="guardarConfiguracion">
        Guardar configuración
      </v-btn>
    </div>

    <v-snackbar v-model="snackbar" color="success" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>
