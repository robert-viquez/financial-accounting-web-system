<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import { fetchAllPages } from "@/api/pagination";
import {
  contabilizarAsiento,
  createAsiento,
  createCuenta,
  createPeriodo,
  getAsientos,
  getCuentasContables,
  getPeriodos,
  updatePeriodo,
} from "@/modules/contabilidad/api/contabilidadService";

const tab = ref("asientos");
const loading = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");
const asientoDialog = ref(false);
const cuentaDialog = ref(false);
const periodoDialog = ref(false);
const asientos = ref([]);
const cuentas = ref([]);
const periodos = ref([]);

const asiento = reactive({
  fecha: new Date().toISOString().slice(0, 10),
  descripcion: "",
  detalles: [],
});
const cuenta = reactive({
  codigo: "",
  nombre: "",
  tipo: "ACTIVO",
  naturaleza: "DEUDORA",
  permite_movimientos: true,
  estado: true,
});
const periodo = reactive({
  nombre: "",
  fecha_inicio: "",
  fecha_fin: "",
});

const totalDebe = computed(() =>
  asiento.detalles.reduce((total, item) => total + Number(item.debe || 0), 0)
);
const totalHaber = computed(() =>
  asiento.detalles.reduce((total, item) => total + Number(item.haber || 0), 0)
);
const balanceado = computed(
  () => totalDebe.value > 0 && totalDebe.value === totalHaber.value
);

function mensaje(texto, color = "success") {
  snackbarText.value = texto;
  snackbarColor.value = color;
  snackbar.value = true;
}

function formatoCRC(value) {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
  }).format(Number(value || 0));
}

async function cargar() {
  loading.value = true;
  try {
    [asientos.value, cuentas.value, periodos.value] = await Promise.all([
      fetchAllPages(getAsientos, { ordering: "-fecha" }),
      fetchAllPages(getCuentasContables, { ordering: "codigo" }),
      fetchAllPages(getPeriodos, {}),
    ]);
  } catch {
    mensaje("No se pudo cargar la información contable.", "error");
  } finally {
    loading.value = false;
  }
}

function abrirAsiento() {
  asiento.fecha = new Date().toISOString().slice(0, 10);
  asiento.descripcion = "";
  asiento.detalles = [
    { cuenta: null, descripcion: "", debe: 0, haber: 0 },
    { cuenta: null, descripcion: "", debe: 0, haber: 0 },
  ];
  asientoDialog.value = true;
}

async function guardarAsiento() {
  if (!asiento.descripcion || !balanceado.value || asiento.detalles.some((d) => !d.cuenta)) {
    mensaje("Complete un asiento balanceado con todas sus cuentas.", "error");
    return;
  }
  try {
    await createAsiento({
      ...asiento,
      detalles: asiento.detalles.map((d) => ({
        ...d,
        debe: Number(d.debe || 0).toFixed(2),
        haber: Number(d.haber || 0).toFixed(2),
      })),
    });
    asientoDialog.value = false;
    mensaje("Asiento guardado como borrador.");
    await cargar();
  } catch (error) {
    mensaje(error.response?.data?.non_field_errors?.[0] || "No se pudo guardar el asiento.", "error");
  }
}

async function contabilizar(item) {
  try {
    await contabilizarAsiento(item.id);
    mensaje("Asiento contabilizado.");
    await cargar();
  } catch (error) {
    mensaje(error.response?.data?.detail || "No se pudo contabilizar.", "error");
  }
}

async function guardarCuenta() {
  try {
    await createCuenta(cuenta);
    cuentaDialog.value = false;
    mensaje("Cuenta creada.");
    await cargar();
  } catch {
    mensaje("No se pudo crear la cuenta.", "error");
  }
}

async function guardarPeriodo() {
  try {
    await createPeriodo(periodo);
    periodoDialog.value = false;
    mensaje("Periodo creado.");
    await cargar();
  } catch (error) {
    mensaje(error.response?.data?.non_field_errors?.[0] || "No se pudo crear el periodo.", "error");
  }
}

async function cambiarEstadoPeriodo(item) {
  try {
    await updatePeriodo(item.id, { cerrado: !item.cerrado });
    mensaje(item.cerrado ? "Periodo reabierto." : "Periodo cerrado.");
    await cargar();
  } catch {
    mensaje("No se pudo actualizar el periodo.", "error");
  }
}

onMounted(cargar);
</script>

<template>
  <section>
    <PageHeader
      title="Contabilidad"
      subtitle="Catálogo, periodos y asientos contables de partida doble."
    />

    <v-tabs v-model="tab" class="mb-4">
      <v-tab value="asientos">Asientos</v-tab>
      <v-tab value="cuentas">Catálogo</v-tab>
      <v-tab value="periodos">Periodos</v-tab>
    </v-tabs>

    <v-card :loading="loading">
      <template v-if="tab === 'asientos'">
        <v-card-title class="d-flex align-center">
          Asientos contables
          <v-spacer />
          <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirAsiento">Nuevo asiento</v-btn>
        </v-card-title>
        <v-table>
          <thead><tr><th>Número</th><th>Fecha</th><th>Descripción</th><th>Origen</th><th>Debe</th><th>Haber</th><th>Estado</th><th /></tr></thead>
          <tbody>
            <tr v-for="item in asientos" :key="item.id">
              <td>{{ item.numero }}</td><td>{{ item.fecha }}</td><td>{{ item.descripcion }}</td>
              <td>{{ item.origen }}</td><td>{{ formatoCRC(item.total_debe) }}</td>
              <td>{{ formatoCRC(item.total_haber) }}</td><td>{{ item.estado }}</td>
              <td><v-btn v-if="item.estado === 'BORRADOR'" size="small" variant="tonal" @click="contabilizar(item)">Contabilizar</v-btn></td>
            </tr>
          </tbody>
        </v-table>
      </template>

      <template v-else-if="tab === 'cuentas'">
        <v-card-title class="d-flex align-center">
          Catálogo de cuentas<v-spacer /><v-btn color="primary" @click="cuentaDialog = true">Nueva cuenta</v-btn>
        </v-card-title>
        <v-table><thead><tr><th>Código</th><th>Nombre</th><th>Tipo</th><th>Naturaleza</th><th>Activa</th></tr></thead>
          <tbody><tr v-for="item in cuentas" :key="item.id"><td>{{ item.codigo }}</td><td>{{ item.nombre }}</td><td>{{ item.tipo }}</td><td>{{ item.naturaleza }}</td><td>{{ item.estado ? "Sí" : "No" }}</td></tr></tbody>
        </v-table>
      </template>

      <template v-else>
        <v-card-title class="d-flex align-center">
          Periodos contables<v-spacer /><v-btn color="primary" @click="periodoDialog = true">Nuevo periodo</v-btn>
        </v-card-title>
        <v-table><thead><tr><th>Nombre</th><th>Inicio</th><th>Fin</th><th>Estado</th><th /></tr></thead>
          <tbody><tr v-for="item in periodos" :key="item.id"><td>{{ item.nombre }}</td><td>{{ item.fecha_inicio }}</td><td>{{ item.fecha_fin }}</td><td>{{ item.cerrado ? "Cerrado" : "Abierto" }}</td><td><v-btn size="small" variant="tonal" @click="cambiarEstadoPeriodo(item)">{{ item.cerrado ? "Reabrir" : "Cerrar" }}</v-btn></td></tr></tbody>
        </v-table>
      </template>
    </v-card>

    <v-dialog v-model="asientoDialog" max-width="1000">
      <v-card><v-card-title>Nuevo asiento manual</v-card-title><v-card-text>
        <v-row><v-col cols="12" md="3"><v-text-field v-model="asiento.fecha" type="date" label="Fecha" /></v-col><v-col cols="12" md="9"><v-text-field v-model="asiento.descripcion" label="Descripción" /></v-col></v-row>
        <v-table><thead><tr><th>Cuenta</th><th>Descripción</th><th>Debe</th><th>Haber</th><th /></tr></thead>
          <tbody><tr v-for="(linea, index) in asiento.detalles" :key="index">
            <td><v-select v-model="linea.cuenta" :items="cuentas.filter((c) => c.permite_movimientos && c.estado)" item-title="nombre" item-value="id" hide-details /></td>
            <td><v-text-field v-model="linea.descripcion" hide-details /></td>
            <td><v-text-field v-model.number="linea.debe" type="number" hide-details /></td>
            <td><v-text-field v-model.number="linea.haber" type="number" hide-details /></td>
            <td><v-btn icon="mdi-delete" variant="text" @click="asiento.detalles.splice(index, 1)" /></td>
          </tr></tbody>
        </v-table>
        <v-btn class="mt-3" variant="tonal" @click="asiento.detalles.push({ cuenta: null, descripcion: '', debe: 0, haber: 0 })">Agregar línea</v-btn>
        <div class="text-right mt-3">Debe: {{ formatoCRC(totalDebe) }} · Haber: {{ formatoCRC(totalHaber) }}</div>
      </v-card-text><v-card-actions><v-spacer /><v-btn @click="asientoDialog = false">Cancelar</v-btn><v-btn color="primary" @click="guardarAsiento">Guardar</v-btn></v-card-actions></v-card>
    </v-dialog>

    <v-dialog v-model="cuentaDialog" max-width="600"><v-card><v-card-title>Nueva cuenta</v-card-title><v-card-text><v-text-field v-model="cuenta.codigo" label="Código" /><v-text-field v-model="cuenta.nombre" label="Nombre" /><v-select v-model="cuenta.tipo" :items="['ACTIVO','PASIVO','PATRIMONIO','INGRESO','GASTO','COSTO']" label="Tipo" /><v-select v-model="cuenta.naturaleza" :items="['DEUDORA','ACREEDORA']" label="Naturaleza" /></v-card-text><v-card-actions><v-spacer /><v-btn @click="cuentaDialog = false">Cancelar</v-btn><v-btn color="primary" @click="guardarCuenta">Guardar</v-btn></v-card-actions></v-card></v-dialog>

    <v-dialog v-model="periodoDialog" max-width="600"><v-card><v-card-title>Nuevo periodo</v-card-title><v-card-text><v-text-field v-model="periodo.nombre" label="Nombre" /><v-text-field v-model="periodo.fecha_inicio" type="date" label="Inicio" /><v-text-field v-model="periodo.fecha_fin" type="date" label="Fin" /></v-card-text><v-card-actions><v-spacer /><v-btn @click="periodoDialog = false">Cancelar</v-btn><v-btn color="primary" @click="guardarPeriodo">Guardar</v-btn></v-card-actions></v-card></v-dialog>

    <v-snackbar v-model="snackbar" :color="snackbarColor">{{ snackbarText }}</v-snackbar>
  </section>
</template>
