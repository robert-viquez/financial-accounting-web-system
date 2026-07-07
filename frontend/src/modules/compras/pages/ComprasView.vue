<script setup>
import { onMounted, ref, watch } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import SearchToolbar from "@/components/common/SearchToolbar.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import CompraDialog from "../components/CompraDialog.vue";
import { useDebounce } from "@/composables/useDebounce";
import { usePersistentFilters } from "@/composables/usePersistentFilters";
import { useServerTable } from "@/composables/useServerTable";

import { getCompras, createCompra, deleteCompra } from "../api/ComprasServices";
import { getProveedores } from "@/modules/proveedores/api/ProveedoresServices";
import { getProductos } from "@/modules/inventario/api/ProductosServices";

const compras = ref([]);
const totalItems = ref(0);
const proveedores = ref([]);
const productos = ref([]);
const loading = ref(false);
const saving = ref(false);
const dialog = ref(false);
const confirmDialog = ref(false);
const compraAEliminar = ref(null);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const { filters } = usePersistentFilters("compras_filters", {
  search: "",
});
const { options, serverParams, updateOptions } = useServerTable({
  ordering: "-fecha",
});

const headers = [
  { title: "Factura", key: "numero_factura", sortable: false },
  { title: "Proveedor", key: "proveedor_nombre", sortable: false },
  { title: "Tipo", key: "tipo_compra", sortable: false },
  { title: "Total", key: "total" },
  { title: "Estado", key: "estado", sortable: false },
  { title: "Fecha", key: "fecha" },
  { title: "Acciones", key: "actions", sortable: false },
];

const debouncedLoad = useDebounce(() => {
  options.page = 1;
  cargarCompras();
});

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

async function cargarCompras() {
  loading.value = true;

  try {
    const response = await getCompras({
      ...serverParams.value,
      search: filters.search || undefined,
    });

    compras.value = response.results ?? response;
    totalItems.value = response.count ?? compras.value.length;
  } catch (error) {
    mostrarMensaje("No se pudieron cargar las compras.", "error");
  } finally {
    loading.value = false;
  }
}

function onTableOptions(value) {
  updateOptions(value);
  cargarCompras();
}

async function cargarCatalogos() {
  try {
    const proveedoresResponse = await getProveedores({ ordering: "nombre" });
    const productosResponse = await getProductos({ ordering: "nombre" });

    proveedores.value = proveedoresResponse.results ?? proveedoresResponse;
    productos.value = productosResponse.results ?? productosResponse;
  } catch (error) {
    mostrarMensaje("No se pudieron cargar los catálogos.", "error");
  }
}

function nuevaCompra() {
  dialog.value = true;
}

async function guardarCompra(data) {
  saving.value = true;

  try {
    await createCompra(data);
    dialog.value = false;
    mostrarMensaje("Compra registrada correctamente.");
    await cargarCompras();
  } catch (error) {
    console.error(error.response?.data || error);
    mostrarMensaje("No se pudo registrar la compra.", "error");
  } finally {
    saving.value = false;
  }
}

function pedirEliminarCompra(item) {
  compraAEliminar.value = item;
  confirmDialog.value = true;
}

async function confirmarEliminarCompra() {
  if (!compraAEliminar.value) return;

  try {
    await deleteCompra(compraAEliminar.value.id);
    mostrarMensaje("Compra eliminada correctamente.");
    confirmDialog.value = false;
    compraAEliminar.value = null;
    await cargarCompras();
  } catch (error) {
    mostrarMensaje("No se pudo eliminar la compra.", "error");
  }
}

watch(() => filters.search, debouncedLoad);

onMounted(async () => {
  await cargarCatalogos();
  await cargarCompras();
});
</script>

<template>
  <section>
    <PageHeader
      title="Compras"
      subtitle="Registro de compras a proveedores y actualización automática del inventario."
      button-text="Nueva compra"
      @click="nuevaCompra"
    />

    <v-card>
      <SearchToolbar
        v-model="filters.search"
        label="Buscar compra"
        @search="cargarCompras"
      />

      <v-skeleton-loader
        v-if="loading && !compras.length"
        type="table"
        class="mx-4 mb-4"
      />

      <v-data-table-server
        v-else
        :headers="headers"
        :items="compras"
        :items-length="totalItems"
        :loading="loading"
        :items-per-page="options.itemsPerPage"
        item-value="id"
        @update:options="onTableOptions"
      >
        <template #item.tipo_compra="{ item }">
          <v-chip
            :color="item.tipo_compra === 'CREDITO' ? 'orange' : 'green'"
            variant="tonal"
            size="small"
          >
            {{ item.tipo_compra === "CREDITO" ? "Crédito" : "Contado" }}
          </v-chip>
        </template>

        <template #item.total="{ item }">
          {{ formatoCRC(item.total) }}
        </template>

        <template #item.estado="{ item }">
          <v-chip
            :color="item.estado === 'REGISTRADA' ? 'green' : 'grey'"
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
            @click="pedirEliminarCompra(item)"
          />
        </template>
      </v-data-table-server>
    </v-card>

    <CompraDialog
      v-model="dialog"
      :proveedores="proveedores"
      :productos="productos"
      :loading="saving"
      @save="guardarCompra"
    />

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar compra"
      :message="`¿Desea eliminar la compra ${compraAEliminar?.numero_factura || ''}?`"
      @confirm="confirmarEliminarCompra"
    />

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>
