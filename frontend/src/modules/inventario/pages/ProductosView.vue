<script setup>
import { ref, onMounted, watch } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import SearchToolbar from "@/components/common/SearchToolbar.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import BarcodeScannerInput from "@/components/common/BarcodeScannerInput.vue";
import { useDebounce } from "@/composables/useDebounce";
import { usePersistentFilters } from "@/composables/usePersistentFilters";
import { useServerTable } from "@/composables/useServerTable";

import ProductoDialog from "../components/ProductoDialog.vue";
import StockChip from "../components/StockChip.vue";

import {
  getProductos,
  createProducto,
  updateProducto,
  deleteProducto,
  getUnidadesMedida,
  registrarEntradaPorCodigo,
} from "../api/ProductosServices";
import { getCategorias } from "../api/CategoriasServices";
import { getConfiguracion } from "@/modules/configuracion/api/configuracionService";

const productos = ref([]);
const totalItems = ref(0);
const categorias = ref([]);
const unidades = ref([]);
const loading = ref(false);
const dialog = ref(false);
const confirmDialog = ref(false);
const editing = ref(false);
const selected = ref({});
const productoAEliminar = ref(null);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");
const entrada = ref({
  codigo: "",
  cantidad: 1,
  costo_unitario: 0,
});
const scanning = ref(false);
const lectorHabilitado = ref(true);

const { filters } = usePersistentFilters("productos_filters", {
  search: "",
});
const { options, serverParams, updateOptions } = useServerTable({
  ordering: "nombre",
});

const headers = [
  { title: "Código", key: "codigo" },
  { title: "Código de barras", key: "codigo_barras", sortable: false },
  { title: "Nombre", key: "nombre" },
  { title: "Categoría", key: "categoria_nombre", sortable: false },
  { title: "Stock", key: "stock_actual" },
  { title: "Precio", key: "precio_venta" },
  { title: "Estado", key: "estado", sortable: false },
  { title: "Acciones", key: "actions", sortable: false },
];

const debouncedLoad = useDebounce(() => {
  options.page = 1;
  cargarProductos();
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

async function cargarProductos() {
  loading.value = true;

  try {
    const response = await getProductos({
      ...serverParams.value,
      search: filters.search || undefined,
    });

    productos.value = response.results ?? response;
    totalItems.value = response.count ?? productos.value.length;
  } catch (error) {
    mostrarMensaje("No se pudieron cargar los productos.", "error");
  } finally {
    loading.value = false;
  }
}

function onTableOptions(value) {
  updateOptions(value);
  cargarProductos();
}

async function cargarCategorias() {
  try {
    const response = await getCategorias();
    categorias.value = response.results ?? response;
  } catch (error) {
    mostrarMensaje("No se pudieron cargar las categorías.", "error");
  }
}

async function cargarUnidades() {
  try {
    const response = await getUnidadesMedida({ ordering: "nombre" });
    unidades.value = response.results ?? response;
  } catch {
    mostrarMensaje("No se pudieron cargar las unidades de medida.", "error");
  }
}

async function registrarEntrada(codigo = entrada.value.codigo) {
  if (!codigo || Number(entrada.value.cantidad) <= 0) {
    mostrarMensaje("Escanee un código e indique una cantidad válida.", "error");
    return;
  }
  scanning.value = true;
  try {
    const producto = await registrarEntradaPorCodigo({
      codigo,
      cantidad: Number(entrada.value.cantidad).toFixed(2),
      costo_unitario: Number(entrada.value.costo_unitario || 0).toFixed(2),
    });
    mostrarMensaje(
      `Entrada registrada: ${producto.nombre}. Existencia actual: ${producto.stock_actual} ${producto.unidad_medida_simbolo || ""}.`
    );
    entrada.value.codigo = "";
    await cargarProductos();
  } catch (error) {
    mostrarMensaje(
      error.response?.data?.detail || "No se pudo registrar la entrada.",
      "error"
    );
  } finally {
    scanning.value = false;
  }
}

function nuevoProducto() {
  editing.value = false;
  selected.value = {};
  dialog.value = true;
}

function editarProducto(item) {
  editing.value = true;
  selected.value = { ...item };
  dialog.value = true;
}

async function guardarProducto(data) {
  try {
    if (editing.value) {
      await updateProducto(selected.value.id, data);
      mostrarMensaje("Producto actualizado correctamente.");
    } else {
      await createProducto(data);
      mostrarMensaje("Producto creado correctamente.");
    }

    dialog.value = false;
    await cargarProductos();
  } catch (error) {
    mostrarMensaje("No se pudo guardar el producto.", "error");
  }
}

function pedirEliminarProducto(item) {
  productoAEliminar.value = item;
  confirmDialog.value = true;
}

async function confirmarEliminarProducto() {
  if (!productoAEliminar.value) return;

  try {
    await deleteProducto(productoAEliminar.value.id);
    mostrarMensaje("Producto eliminado correctamente.");
    confirmDialog.value = false;
    productoAEliminar.value = null;
    await cargarProductos();
  } catch (error) {
    mostrarMensaje("No se pudo eliminar el producto.", "error");
  }
}

watch(() => filters.search, debouncedLoad);

onMounted(async () => {
  await Promise.all([
    cargarCategorias(),
    cargarUnidades(),
    getConfiguracion()
      .then((config) => {
        lectorHabilitado.value = config.lector_codigo_barras !== false;
      })
      .catch(() => {}),
  ]);
  await cargarProductos();
});
</script>

<template>
  <section>
    <PageHeader
      title="Productos"
      subtitle="Administración del catálogo de productos e inventario."
      button-text="Nuevo producto"
      @click="nuevoProducto"
    />

    <v-card v-if="lectorHabilitado" class="scanner-card mb-4" variant="tonal">
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-barcode-scan" />
        Entrada rápida con lector
      </v-card-title>
      <v-card-subtitle>
        El lector funciona como teclado: escanee y presione Enter.
      </v-card-subtitle>
      <v-card-text>
        <div class="scanner-grid">
          <BarcodeScannerInput
            label="Escanee el producto"
            :loading="scanning"
            @scan="registrarEntrada"
          />
          <v-text-field
            v-model.number="entrada.cantidad"
            label="Cantidad que ingresa"
            type="number"
            min="0.01"
            step="0.01"
            variant="outlined"
            density="comfortable"
            hide-details
          />
          <v-text-field
            v-model.number="entrada.costo_unitario"
            label="Costo unitario"
            type="number"
            min="0"
            prefix="₡"
            variant="outlined"
            density="comfortable"
            hide-details
          />
        </div>
      </v-card-text>
    </v-card>

    <v-card>
      <SearchToolbar
        v-model="filters.search"
        label="Buscar producto"
        @search="cargarProductos"
      />

      <v-skeleton-loader
        v-if="loading && !productos.length"
        type="table"
        class="mx-4 mb-4"
      />

      <v-data-table-server
        v-else
        :headers="headers"
        :items="productos"
        :items-length="totalItems"
        :loading="loading"
        :items-per-page="options.itemsPerPage"
        item-value="id"
        @update:options="onTableOptions"
      >
        <template #item.stock_actual="{ item }">
          <div class="d-flex align-center ga-1">
            <StockChip :stock="Number(item.stock_actual)" />
            <span class="text-caption">{{ item.unidad_medida_simbolo }}</span>
          </div>
        </template>

        <template #item.precio_venta="{ item }">
          {{ formatoCRC(item.precio_venta) }}
        </template>

        <template #item.estado="{ item }">
          <v-chip
            :color="item.estado ? 'green' : 'grey'"
            variant="tonal"
            size="small"
          >
            {{ item.estado ? "Activo" : "Inactivo" }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-pencil"
            variant="text"
            size="small"
            @click="editarProducto(item)"
          />

          <v-btn
            icon="mdi-delete"
            color="error"
            variant="text"
            size="small"
            @click="pedirEliminarProducto(item)"
          />
        </template>
      </v-data-table-server>
    </v-card>

    <ProductoDialog
      v-model="dialog"
      :producto="selected"
      :categorias="categorias"
      :unidades="unidades"
      :editing="editing"
      @save="guardarProducto"
    />

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar producto"
      :message="`¿Desea eliminar el producto ${productoAEliminar?.nombre || ''}?`"
      @confirm="confirmarEliminarProducto"
    />

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>

<style scoped>
.scanner-card {
  overflow: visible;
}

.scanner-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(260px, 2fr) minmax(170px, 1fr) minmax(170px, 1fr);
}

@media (max-width: 959px) {
  .scanner-grid {
    grid-template-columns: 1fr 1fr;
  }

  .scanner-grid > :first-child {
    grid-column: 1 / -1;
  }
}

@media (max-width: 599px) {
  .scanner-grid {
    grid-template-columns: 1fr;
  }

  .scanner-grid > :first-child {
    grid-column: auto;
  }
}
</style>
