<script setup>
import { ref, onMounted, watch } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import SearchToolbar from "@/components/common/SearchToolbar.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
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
} from "../api/ProductosServices";
import { getCategorias } from "../api/CategoriasServices";

const productos = ref([]);
const totalItems = ref(0);
const categorias = ref([]);
const loading = ref(false);
const dialog = ref(false);
const confirmDialog = ref(false);
const editing = ref(false);
const selected = ref({});
const productoAEliminar = ref(null);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const { filters } = usePersistentFilters("productos_filters", {
  search: "",
});
const { options, serverParams, updateOptions } = useServerTable({
  ordering: "nombre",
});

const headers = [
  { title: "Código", key: "codigo" },
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
  await cargarCategorias();
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
          <StockChip :stock="Number(item.stock_actual)" />
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
