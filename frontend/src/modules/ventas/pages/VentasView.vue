<script setup>
import { onMounted, ref, watch } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import SearchToolbar from "@/components/common/SearchToolbar.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import VentaDialog from "../components/VentaDialog.vue";
import { useDebounce } from "@/composables/useDebounce";
import { usePersistentFilters } from "@/composables/usePersistentFilters";
import { useServerTable } from "@/composables/useServerTable";

import { createVenta, deleteVenta, getVentas } from "../api/ventasService";
import { getClientes } from "@/modules/clientes/api/ClientesServices";
import { getProductos } from "@/modules/inventario/api/ProductosServices";
import { getMediosPago } from "@/modules/terceros/api/MediosPagoServices";

const ventas = ref([]);
const totalItems = ref(0);
const clientes = ref([]);
const productos = ref([]);
const mediosPago = ref([]);
const loading = ref(false);
const saving = ref(false);
const dialog = ref(false);
const confirmDialog = ref(false);
const ventaAEliminar = ref(null);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const { filters } = usePersistentFilters("ventas_filters", {
  search: "",
});
const { options, serverParams, updateOptions } = useServerTable({
  ordering: "-fecha",
});

const headers = [
  { title: "Comprobante", key: "numero_comprobante", sortable: false },
  { title: "Cliente", key: "cliente_nombre", sortable: false },
  { title: "Tipo", key: "tipo_venta", sortable: false },
  { title: "Medio pago", key: "medio_pago_nombre", sortable: false },
  { title: "Total", key: "total" },
  { title: "Estado", key: "estado", sortable: false },
  { title: "Fecha", key: "fecha" },
  { title: "Acciones", key: "actions", sortable: false },
];

const debouncedLoad = useDebounce(() => {
  options.page = 1;
  cargarVentas();
});

function mostrarMensaje(texto, color = "success") {
  snackbarText.value = texto;
  snackbarColor.value = color;
  snackbar.value = true;
}

function obtenerMensajeError(error, fallback) {
  const data = error?.response?.data;

  if (!data) return fallback;
  if (typeof data === "string") return data;
  if (Array.isArray(data)) {
    return data.map((item) => obtenerTextoError(item)).join(" ");
  }
  if (data.detail) return data.detail;
  if (data.non_field_errors) {
    return data.non_field_errors.map((item) => obtenerTextoError(item)).join(" ");
  }

  const firstFieldError = Object.values(data).flat().find(Boolean);
  return firstFieldError ? obtenerTextoError(firstFieldError) : fallback;
}

function obtenerTextoError(value) {
  if (!value) return "";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map((item) => obtenerTextoError(item)).join(" ");
  if (typeof value === "object") {
    return Object.values(value)
      .flat()
      .map((item) => obtenerTextoError(item))
      .filter(Boolean)
      .join(" ");
  }

  return String(value);
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

function etiquetaTipoVenta(tipo) {
  return tipo === "CREDITO" ? "Crédito" : "Contado";
}

function colorTipoVenta(tipo) {
  return tipo === "CREDITO" ? "orange" : "green";
}

function etiquetaEstado(estado) {
  const estados = {
    EMITIDA: "Emitida",
    ANULADA: "Anulada",
  };

  return estados[estado] || estado;
}

function colorEstado(estado) {
  return estado === "EMITIDA" ? "green" : "grey";
}

async function cargarVentas() {
  loading.value = true;

  try {
    const response = await getVentas({
      ...serverParams.value,
      search: filters.search || undefined,
    });

    ventas.value = response.results ?? response;
    totalItems.value = response.count ?? ventas.value.length;
  } catch (error) {
    mostrarMensaje(
      obtenerMensajeError(error, "No se pudieron cargar las ventas."),
      "error"
    );
  } finally {
    loading.value = false;
  }
}

function onTableOptions(value) {
  updateOptions(value);
  cargarVentas();
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
    mostrarMensaje(
      obtenerMensajeError(error, "No se pudieron cargar los catálogos."),
      "error"
    );
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

    const mensaje =
      data.tipo_venta === "CREDITO"
        ? "Venta a crédito registrada. Se creó la cuenta por cobrar automáticamente."
        : "Venta registrada correctamente. El inventario fue actualizado.";

    mostrarMensaje(mensaje);
    await Promise.all([cargarCatalogos(), cargarVentas()]);
  } catch (error) {
    console.error(error.response?.data || error);
    mostrarMensaje(
      obtenerMensajeError(error, "No se pudo registrar la venta."),
      "error"
    );
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
    await Promise.all([cargarCatalogos(), cargarVentas()]);
  } catch (error) {
    mostrarMensaje(
      obtenerMensajeError(error, "No se pudo eliminar la venta."),
      "error"
    );
  }
}

watch(() => filters.search, debouncedLoad);

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
      <SearchToolbar
        v-model="filters.search"
        label="Buscar por comprobante o cliente"
        @search="cargarVentas"
      />

      <v-skeleton-loader
        v-if="loading && !ventas.length"
        type="table"
        class="mx-4 mb-4"
      />

      <v-data-table-server
        v-else
        :headers="headers"
        :items="ventas"
        :items-length="totalItems"
        :loading="loading"
        :items-per-page="options.itemsPerPage"
        item-value="id"
        @update:options="onTableOptions"
      >
        <template #item.cliente_nombre="{ item }">
          {{ item.cliente_nombre || "Consumidor final" }}
        </template>

        <template #item.medio_pago_nombre="{ item }">
          {{ item.medio_pago_nombre || "-" }}
        </template>

        <template #item.tipo_venta="{ item }">
          <v-chip
            :color="colorTipoVenta(item.tipo_venta)"
            variant="tonal"
            size="small"
          >
            {{ etiquetaTipoVenta(item.tipo_venta) }}
          </v-chip>
        </template>

        <template #item.total="{ item }">
          {{ formatoCRC(item.total) }}
        </template>

        <template #item.estado="{ item }">
          <v-chip
            :color="colorEstado(item.estado)"
            variant="tonal"
            size="small"
          >
            {{ etiquetaEstado(item.estado) }}
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
      </v-data-table-server>
    </v-card>

    <VentaDialog
      v-model="dialog"
      :clientes="clientes"
      :productos="productos"
      :medios-pago="mediosPago"
      :loading="saving"
      @save="guardarVenta"
      @validation-error="mostrarMensaje($event, 'error')"
    />

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar venta"
      :message="`¿Desea eliminar la venta ${ventaAEliminar?.numero_comprobante || ''}?`"
      @confirm="confirmarEliminarVenta"
    />

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>
