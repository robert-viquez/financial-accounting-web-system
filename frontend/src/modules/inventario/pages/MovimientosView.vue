<script setup>
import { onMounted, ref, watch } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import { useDebounce } from "@/composables/useDebounce";
import { usePersistentFilters } from "@/composables/usePersistentFilters";
import { getMovimientos } from "@/modules/inventario/api/MovimientosServices";
import { getProductos } from "@/modules/inventario/api/ProductosServices";

const movimientos = ref([]);
const productos = ref([]);
const loading = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");

const { filters, resetFilters } = usePersistentFilters("movimientos_filters", {
  producto: null,
  tipo: null,
  fecha_desde: "",
  fecha_hasta: "",
});
const debouncedLoad = useDebounce(cargarMovimientos);

const headers = [
  { title: "Fecha", key: "fecha" },
  { title: "Producto", key: "producto_nombre" },
  { title: "Tipo", key: "tipo" },
  { title: "Cantidad", key: "cantidad" },
  { title: "Usuario", key: "usuario_nombre" },
  { title: "Compra relacionada", key: "compra_relacionada" },
  { title: "Venta relacionada", key: "venta_relacionada" },
  { title: "Descripción", key: "descripcion" },
];

const tipos = [
  { title: "Entrada", value: "ENTRADA" },
  { title: "Salida", value: "SALIDA" },
  { title: "Ajuste", value: "AJUSTE" },
];

function normalizar(response) {
  return response.results ?? response;
}

function formatoFecha(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("es-CR");
}

function formatoNumero(value) {
  return new Intl.NumberFormat("es-CR", {
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function colorTipo(tipo) {
  return {
    ENTRADA: "green",
    SALIDA: "red",
    AJUSTE: "blue",
  }[tipo] || "grey";
}

async function cargarMovimientos() {
  loading.value = true;

  try {
    const response = await getMovimientos({
      producto: filters.producto || undefined,
      tipo: filters.tipo || undefined,
      fecha_desde: filters.fecha_desde || undefined,
      fecha_hasta: filters.fecha_hasta || undefined,
      ordering: "-fecha",
    });

    movimientos.value = normalizar(response);
  } catch (error) {
    snackbarText.value = "No se pudieron cargar los movimientos.";
    snackbar.value = true;
  } finally {
    loading.value = false;
  }
}

async function cargarProductos() {
  const response = await getProductos({ ordering: "nombre" });
  productos.value = normalizar(response);
}

function limpiarFiltros() {
  resetFilters();
  cargarMovimientos();
}

watch(filters, debouncedLoad, { deep: true });

onMounted(async () => {
  await Promise.all([cargarProductos(), cargarMovimientos()]);
});
</script>

<template>
  <section>
    <PageHeader
      title="Movimientos de inventario"
      subtitle="Auditoría de entradas, salidas y ajustes del inventario."
    />

    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.producto"
              :items="productos"
              item-title="nombre"
              item-value="id"
              label="Producto"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-select
              v-model="filters.tipo"
              :items="tipos"
              label="Tipo"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model="filters.fecha_desde"
              label="Desde"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model="filters.fecha_hasta"
              label="Hasta"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="6" md="auto">
            <v-btn block color="primary" variant="tonal" @click="cargarMovimientos">
              Filtrar
            </v-btn>
          </v-col>
          <v-col cols="12" sm="6" md="auto">
            <v-btn block variant="text" @click="limpiarFiltros">Limpiar</v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card>
      <v-data-table
        :headers="headers"
        :items="movimientos"
        :loading="loading"
        item-value="id"
      >
        <template #item.fecha="{ item }">
          {{ formatoFecha(item.fecha) }}
        </template>

        <template #item.tipo="{ item }">
          <v-chip :color="colorTipo(item.tipo)" variant="tonal" size="small">
            {{ item.tipo }}
          </v-chip>
        </template>

        <template #item.cantidad="{ item }">
          {{ formatoNumero(item.cantidad) }}
        </template>
      </v-data-table>
    </v-card>

    <v-snackbar v-model="snackbar" color="error" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>
