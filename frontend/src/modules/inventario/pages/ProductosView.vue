<script setup>
import { ref, onMounted, watch } from "vue";

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
const categorias = ref([]);

const loading = ref(false);

const dialog = ref(false);

const editing = ref(false);

const selected = ref({});

const search = ref("");

const headers = [
  { title: "Código", key: "codigo" },
  { title: "Nombre", key: "nombre" },
  { title: "Categoría", key: "categoria_nombre" },
  { title: "Stock", key: "stock" },
  { title: "Precio", key: "precio_venta" },
  { title: "Estado", key: "estado" },
  { title: "Acciones", key: "actions", sortable: false },
];

async function cargarProductos() {
  loading.value = true;

  try {
    const response = await getProductos({
      search: search.value,
      ordering: "nombre",
    });

    console.log("Respuesta API:", response);

    productos.value = response.results ?? response;

    console.log("Productos:", productos.value);
  } finally {
    loading.value = false;
  }
}

async function cargarCategorias() {
  categorias.value = await getCategorias();
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
  if (editing.value) {
    await updateProducto(selected.value.id, data);
  } else {
    await createProducto(data);
  }

  dialog.value = false;

  await cargarProductos();
}

async function eliminarProducto(item) {
  if (!confirm(`¿Eliminar ${item.nombre}?`)) return;

  await deleteProducto(item.id);

  await cargarProductos();
}

watch(search, cargarProductos);

onMounted(async () => {
  await cargarCategorias();
  await cargarProductos();
});
</script>

<template>
  <v-container fluid>

    <v-row class="mb-4">

      <v-col>

        <h2>Inventario</h2>

      </v-col>

      <v-col class="text-right">

        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="nuevoProducto"
        >
          Nuevo Producto
        </v-btn>

      </v-col>

    </v-row>

    <v-card>

      <v-card-text>

        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Buscar producto..."
          variant="outlined"
          density="comfortable"
        />

      </v-card-text>

      <v-data-table
        :headers="headers"
        :items="productos"
        :loading="loading"
      >

        <template #item.stock="{ item }">
          <StockChip :stock="item.stock" />
        </template>

        <template #item.precio_venta="{ item }">
          ₡ {{ Number(item.precio_venta).toLocaleString() }}
        </template>

        <template #item.estado="{ item }">

          <v-chip
            :color="item.estado ? 'green' : 'grey'"
            variant="tonal"
          >
            {{ item.estado ? "Activo" : "Inactivo" }}
          </v-chip>

        </template>

        <template #item.actions="{ item }">

          <v-btn
            icon="mdi-pencil"
            variant="text"
            @click="editarProducto(item)"
          />

          <v-btn
            icon="mdi-delete"
            color="red"
            variant="text"
            @click="eliminarProducto(item)"
          />

        </template>

      </v-data-table>

    </v-card>

    <ProductoDialog
      v-model="dialog"
      :producto="selected"
      :categorias="categorias"
      :editing="editing"
      @save="guardarProducto"
    />

  </v-container>
</template>