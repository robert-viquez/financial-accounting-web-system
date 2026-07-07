<script setup>
import { onMounted, ref } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import VentaDialog from "../components/VentaDialog.vue";

import {
  getVentas,
  createVenta,
  deleteVenta,
} from "../api/VentasServices";

import { getClientes } from "@/modules/clientes/api/ClientesServices";
import { getProductos } from "@/modules/inventario/api/ProductosServices";
import { getMediosPago } from "@/modules/terceros/api/MediosPagoServices";

const ventas = ref([]);
const clientes = ref([]);
const productos = ref([]);
const mediosPago = ref([]);

const loading = ref(false);
const saving = ref(false);

const dialog = ref(false);
const confirmDialog = ref(false);
const ventaAEliminar = ref(null);

const search = ref("");

const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const headers = [
  { title: "Comprobante", key: "numero_comprobante" },
  { title: "Cliente", key: "cliente_nombre" },
  { title: "Tipo", key: "tipo_venta" },
  { title: "Medio pago", key: "medio_pago_nombre" },
  { title: "Total", key: "total" },
  { title: "Estado", key: "estado" },
  { title: "Fecha", key: "fecha" },
  { title: "Acciones", key: "actions", sortable: false },
];

function mostrarMensaje(texto, color = "success") {
  snackbarText.value = texto;
  snackbarColor.value = color;
  snackbar.value = true;
}

function formatoCRC(valor) {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
  }).format(Number(valor || 0));
}

function formatoFecha(fecha) {
  if (!fecha) return "";
  return new Date(fecha).toLocaleString("es-CR");
}

async function cargarVentas() {
  loading.value = true;

  try {
    const response = await getVentas({
      search: search.value || undefined,
      ordering: "-fecha",
    });

    ventas.value = response.results ?? response;
  } catch (error) {
    mostrarMensaje("No se pudieron cargar las ventas.", "error");
  } finally {
    loading.value = false;
  }
}

async function cargarCatalogos() {
  try {
    const clientesResponse = await getClientes({ ordering: "nombre" });
    const productosResponse = await getProductos({ ordering: "nombre" });
    const mediosPagoResponse = await getMediosPago({ ordering: "nombre" });

    clientes.value = clientesResponse.results ?? clientesResponse;
    productos.value = productosResponse.results ?? productosResponse;
    mediosPago.value = mediosPagoResponse.results ?? mediosPagoResponse;
  } catch (error) {
    mostrarMensaje("No se pudieron cargar los catálogos.", "error");
  }
}

function nuevaVenta() {
  dialog.value = true;
}

async function guardarVenta(data) {
  saving.value = true;

  try {
    await createVenta(data);

    dialog.value = false;

    mostrarMensaje("Venta registrada correctamente.");

    await cargarVentas();
  } catch (error) {
    console.error(error.response?.data || error);
    mostrarMensaje("No se pudo registrar la venta.", "error");
  } finally {
    saving.value = false;
  }
}

function pedirEliminarVenta(item) {
  ventaAEliminar.value = item;
  confirmDialog.value = true;
}

async function confirmarEliminarVenta() {
  if (!ventaAEliminar.value) return;

  try {
    await deleteVenta(ventaAEliminar.value.id);

    mostrarMensaje("Venta eliminada correctamente.");

    confirmDialog.value = false;
    ventaAEliminar.value = null;

    await cargarVentas();
  } catch (error) {
    mostrarMensaje("No se pudo eliminar la venta.", "error");
  }
}

onMounted(async () => {
  await cargarCatalogos();
  await cargarVentas();
});
</script>

<template>
  <section>
    <PageHeader
      title="Ventas"
      subtitle="Registro de ventas y actualización automática del inventario."
      button-text="Nueva venta"
      @click="nuevaVenta"
    />

    <v-card>
      <v-card-text>
        <v-text-field
          v-model="search"
          label="Buscar venta"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          hide-details
          @keyup.enter="cargarVentas"
          @click:clear="cargarVentas"
        />
      </v-card-text>

      <v-data-table
        :headers="headers"
        :items="ventas"
        :loading="loading"
        item-value="id"
      >
        <template #item.tipo_venta="{ item }">
          <v-chip
            :color="item.tipo_venta === 'CREDITO' ? 'orange' : 'green'"
            variant="tonal"
            size="small"
          >
            {{ item.tipo_venta === "CREDITO" ? "Crédito" : "Contado" }}
          </v-chip>
        </template>

        <template #item.total="{ item }">
          {{ formatoCRC(item.total) }}
        </template>

        <template #item.estado="{ item }">
          <v-chip
            :color="item.estado === 'EMITIDA' ? 'green' : 'grey'"
            variant="tonal"
            size="small"
          >
            {{ item.estado }}
          </v-chip>
        </template>

        <template #item.fecha="{ item }">
          {{ formatoFecha(item.fecha) }}
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-delete"
            variant="text"
            color="error"
            size="small"
            @click="pedirEliminarVenta(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <VentaDialog
      v-model="dialog"
      :clientes="clientes"
      :productos="productos"
      :medios-pago="mediosPago"
      :loading="saving"
      @save="guardarVenta"
    />

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar venta"
      :message="`¿Desea eliminar la venta ${ventaAEliminar?.numero_comprobante || ''}?`"
      @confirm="confirmarEliminarVenta"
    />

    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      timeout="3000"
    >
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>