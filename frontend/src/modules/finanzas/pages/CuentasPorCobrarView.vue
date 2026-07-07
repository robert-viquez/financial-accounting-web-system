<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import PageHeader from "@/components/common/PageHeader.vue";
import {
  createPagoCliente,
  deleteCuentaPorCobrar,
  getCuentasPorCobrar,
  getPagosClientes,
} from "@/modules/finanzas/api/finanzasService";
import { getMediosPago } from "@/modules/terceros/api/MediosPagoServices";

const cuentas = ref([]);
const pagos = ref([]);
const mediosPago = ref([]);
const loading = ref(false);
const saving = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");
const confirmDialog = ref(false);
const pagoDialog = ref(false);
const historialDialog = ref(false);
const cuentaSeleccionada = ref(null);

const filters = reactive({
  search: "",
  estado: null,
});

const pagoForm = reactive({
  medio_pago: null,
  monto: 0,
  referencia: "",
  observaciones: "",
});

const headers = [
  { title: "Venta", key: "venta_numero" },
  { title: "Cliente", key: "cliente_nombre" },
  { title: "Emisión", key: "fecha_emision" },
  { title: "Vence", key: "fecha_vencimiento" },
  { title: "Monto", key: "monto_original" },
  { title: "Saldo", key: "saldo" },
  { title: "Estado", key: "estado_calculado" },
  { title: "Acciones", key: "actions", sortable: false },
];

const estados = [
  { title: "Pendiente", value: "PENDIENTE" },
  { title: "Pagada", value: "PAGADA" },
  { title: "Vencida", value: "VENCIDA" },
  { title: "Parcial", value: "PARCIAL" },
];

const pagosCuenta = computed(() =>
  pagos.value.filter(
    (pago) => pago.cuenta_por_cobrar === cuentaSeleccionada.value?.id
  )
);

function normalizar(response) {
  return response.results ?? response;
}

function mostrarMensaje(texto, color = "success") {
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

function formatoFecha(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("es-CR");
}

function estadoCalculado(cuenta) {
  if (cuenta.estado === "PAGADA") return "PAGADA";
  if (Number(cuenta.saldo || 0) <= 0) return "PAGADA";
  if (new Date(cuenta.fecha_vencimiento) < inicioHoy()) return "VENCIDA";
  return cuenta.estado;
}

function estadoLabel(estado) {
  return {
    PENDIENTE: "Pendiente",
    PARCIAL: "Parcial",
    PAGADA: "Pagada",
    ANULADA: "Anulada",
    VENCIDA: "Vencida",
  }[estado] || estado;
}

function estadoColor(estado) {
  return {
    PENDIENTE: "orange",
    PARCIAL: "blue",
    PAGADA: "green",
    ANULADA: "grey",
    VENCIDA: "red",
  }[estado] || "grey";
}

function inicioHoy() {
  const date = new Date();
  date.setHours(0, 0, 0, 0);
  return date;
}

async function cargarCuentas() {
  loading.value = true;

  try {
    const params = {
      search: filters.search || undefined,
      ordering: "fecha_vencimiento",
    };

    if (filters.estado && filters.estado !== "VENCIDA") {
      params.estado = filters.estado;
    }

    const response = await getCuentasPorCobrar(params);
    const data = normalizar(response);
    cuentas.value =
      filters.estado === "VENCIDA"
        ? data.filter((cuenta) => estadoCalculado(cuenta) === "VENCIDA")
        : data;
  } catch (error) {
    mostrarMensaje("No se pudieron cargar las cuentas por cobrar.", "error");
  } finally {
    loading.value = false;
  }
}

async function cargarCatalogos() {
  const [mediosPagoResponse, pagosResponse] = await Promise.all([
    getMediosPago({ ordering: "nombre" }),
    getPagosClientes({ ordering: "-fecha" }),
  ]);

  mediosPago.value = normalizar(mediosPagoResponse);
  pagos.value = normalizar(pagosResponse);
}

function abrirPago(cuenta) {
  cuentaSeleccionada.value = cuenta;
  pagoForm.medio_pago = null;
  pagoForm.monto = Number(cuenta.saldo || 0);
  pagoForm.referencia = "";
  pagoForm.observaciones = "";
  pagoDialog.value = true;
}

function abrirHistorial(cuenta) {
  cuentaSeleccionada.value = cuenta;
  historialDialog.value = true;
}

function pedirEliminar(cuenta) {
  cuentaSeleccionada.value = cuenta;
  confirmDialog.value = true;
}

async function registrarPago() {
  if (!cuentaSeleccionada.value) return;
  if (!pagoForm.medio_pago || Number(pagoForm.monto) <= 0) {
    mostrarMensaje("Complete el medio de pago y un monto válido.", "error");
    return;
  }

  saving.value = true;

  try {
    await createPagoCliente({
      cuenta_por_cobrar: cuentaSeleccionada.value.id,
      medio_pago: pagoForm.medio_pago,
      monto: Number(pagoForm.monto).toFixed(2),
      referencia: pagoForm.referencia,
      observaciones: pagoForm.observaciones,
    });

    pagoDialog.value = false;
    mostrarMensaje("Abono registrado correctamente.");
    await Promise.all([cargarCuentas(), cargarCatalogos()]);
  } catch (error) {
    mostrarMensaje("No se pudo registrar el abono.", "error");
  } finally {
    saving.value = false;
  }
}

async function confirmarEliminar() {
  if (!cuentaSeleccionada.value) return;

  try {
    await deleteCuentaPorCobrar(cuentaSeleccionada.value.id);
    confirmDialog.value = false;
    cuentaSeleccionada.value = null;
    mostrarMensaje("Cuenta eliminada correctamente.");
    await cargarCuentas();
  } catch (error) {
    mostrarMensaje("No se pudo eliminar la cuenta.", "error");
  }
}

onMounted(async () => {
  await Promise.all([cargarCuentas(), cargarCatalogos()]);
});
</script>

<template>
  <section>
    <PageHeader
      title="Cuentas por cobrar"
      subtitle="Control de saldos pendientes, vencimientos y abonos de clientes."
    />

    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="5">
            <v-text-field
              v-model="filters.search"
              label="Buscar cliente o venta"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              @keyup.enter="cargarCuentas"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="filters.estado"
              :items="estados"
              label="Estado"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>

          <v-col cols="12" sm="6" md="auto">
            <v-btn block color="primary" variant="tonal" @click="cargarCuentas">
              Filtrar
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card>
      <v-data-table
        :headers="headers"
        :items="cuentas"
        :loading="loading"
        item-value="id"
      >
        <template #item.fecha_emision="{ item }">
          {{ formatoFecha(item.fecha_emision) }}
        </template>

        <template #item.fecha_vencimiento="{ item }">
          {{ formatoFecha(item.fecha_vencimiento) }}
        </template>

        <template #item.monto_original="{ item }">
          {{ formatoCRC(item.monto_original) }}
        </template>

        <template #item.saldo="{ item }">
          <strong>{{ formatoCRC(item.saldo) }}</strong>
        </template>

        <template #item.estado_calculado="{ item }">
          <v-chip
            :color="estadoColor(estadoCalculado(item))"
            variant="tonal"
            size="small"
          >
            {{ estadoLabel(estadoCalculado(item)) }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-cash-plus"
            variant="text"
            size="small"
            :disabled="estadoCalculado(item) === 'PAGADA'"
            @click="abrirPago(item)"
          />
          <v-btn
            icon="mdi-history"
            variant="text"
            size="small"
            @click="abrirHistorial(item)"
          />
          <v-btn
            icon="mdi-delete"
            color="error"
            variant="text"
            size="small"
            @click="pedirEliminar(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="pagoDialog" max-width="520">
      <v-card>
        <v-card-title>Registrar abono</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-text-field
                :model-value="cuentaSeleccionada?.cliente_nombre"
                label="Cliente"
                variant="outlined"
                density="compact"
                readonly
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                :model-value="formatoCRC(cuentaSeleccionada?.saldo)"
                label="Saldo pendiente"
                variant="outlined"
                density="compact"
                readonly
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model.number="pagoForm.monto"
                label="Monto"
                type="number"
                prefix="₡"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="pagoForm.medio_pago"
                :items="mediosPago"
                item-title="nombre"
                item-value="id"
                label="Medio de pago"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="pagoForm.referencia"
                label="Referencia"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="pagoForm.observaciones"
                label="Observaciones"
                variant="outlined"
                density="compact"
                rows="2"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="pagoDialog = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="saving" @click="registrarPago">
            Guardar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="historialDialog" max-width="720">
      <v-card>
        <v-card-title>Historial de abonos</v-card-title>
        <v-table density="compact">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Medio</th>
              <th>Referencia</th>
              <th class="text-right">Monto</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pago in pagosCuenta" :key="pago.id">
              <td>{{ formatoFecha(pago.fecha) }}</td>
              <td>{{ pago.medio_pago_nombre }}</td>
              <td>{{ pago.referencia || "-" }}</td>
              <td class="text-right">{{ formatoCRC(pago.monto) }}</td>
            </tr>
          </tbody>
        </v-table>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="historialDialog = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar cuenta"
      :message="`¿Desea eliminar la cuenta ${cuentaSeleccionada?.venta_numero || ''}?`"
      @confirm="confirmarEliminar"
    />

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>
