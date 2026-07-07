<script setup>
import { computed, onMounted, ref } from "vue";

import { getVentas } from "@/modules/ventas/api/ventasService";
import { getCompras } from "@/modules/compras/api/ComprasServices";
import { getProductos } from "@/modules/inventario/api/ProductosServices";
import { getClientes } from "@/modules/clientes/api/ClientesServices";
import { getProveedores } from "@/modules/proveedores/api/ProveedoresServices";
import {
  getCuentasPorCobrar,
  getCuentasPorPagar,
} from "@/modules/finanzas/api/finanzasService";

const loading = ref(false);
const snackbar = ref(false);
const snackbarText = ref("");
const ventas = ref([]);
const compras = ref([]);
const productos = ref([]);
const clientes = ref([]);
const proveedores = ref([]);
const cuentasPorCobrar = ref([]);
const cuentasPorPagar = ref([]);

const hoy = new Date();
const mesActual = hoy.getMonth();
const anioActual = hoy.getFullYear();

const kpis = computed(() => [
  {
    title: "Ventas del día",
    value: formatoCRC(totalVentasDia.value),
    icon: "mdi-cash-register",
    color: "green",
  },
  {
    title: "Ventas del mes",
    value: formatoCRC(totalVentasMes.value),
    icon: "mdi-trending-up",
    color: "blue",
  },
  {
    title: "Compras del mes",
    value: formatoCRC(totalComprasMes.value),
    icon: "mdi-cart-arrow-down",
    color: "deep-orange",
  },
  {
    title: "Productos registrados",
    value: productos.value.length,
    icon: "mdi-package-variant-closed",
    color: "indigo",
  },
  {
    title: "Stock bajo",
    value: productosStockBajo.value.length,
    icon: "mdi-alert-circle-outline",
    color: "red",
  },
  {
    title: "Clientes",
    value: clientes.value.length,
    icon: "mdi-account-group",
    color: "teal",
  },
  {
    title: "Proveedores",
    value: proveedores.value.length,
    icon: "mdi-truck-delivery",
    color: "purple",
  },
]);

const totalVentasDia = computed(() =>
  ventas.value
    .filter((venta) => esMismaFecha(venta.fecha, hoy))
    .reduce((sum, venta) => sum + numero(venta.total), 0)
);

const totalVentasMes = computed(() =>
  ventas.value
    .filter((venta) => esMismoMes(venta.fecha, anioActual, mesActual))
    .reduce((sum, venta) => sum + numero(venta.total), 0)
);

const totalComprasMes = computed(() =>
  compras.value
    .filter((compra) => esMismoMes(compra.fecha, anioActual, mesActual))
    .reduce((sum, compra) => sum + numero(compra.total), 0)
);

const productosStockBajo = computed(() =>
  productos.value
    .filter((producto) => numero(producto.stock_actual) <= numero(producto.stock_minimo))
    .sort((a, b) => numero(a.stock_actual) - numero(b.stock_actual))
);

const ventasPorMes = computed(() =>
  serieMensual(ventas.value, "fecha", "total", "Ventas")
);

const comprasPorMes = computed(() =>
  serieMensual(compras.value, "fecha", "total", "Compras")
);

const productosMasVendidos = computed(() => {
  const acumulado = new Map();

  ventas.value.forEach((venta) => {
    (venta.detalles || []).forEach((detalle) => {
      const key = detalle.producto;
      const actual = acumulado.get(key) || {
        label: detalle.producto_nombre || "Producto",
        value: 0,
      };

      actual.value += numero(detalle.cantidad);
      acumulado.set(key, actual);
    });
  });

  return Array.from(acumulado.values())
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);
});

const productosMenorStock = computed(() =>
  productos.value
    .map((producto) => ({
      label: producto.nombre,
      value: numero(producto.stock_actual),
      meta: `Mínimo ${formatoNumero(producto.stock_minimo)}`,
    }))
    .sort((a, b) => a.value - b.value)
    .slice(0, 5)
);

const ultimasVentas = computed(() => ventas.value.slice(0, 5));
const ultimasCompras = computed(() => compras.value.slice(0, 5));
const cuentasPorCobrarPendientes = computed(() => cuentasPorCobrar.value.slice(0, 5));
const cuentasPorPagarPendientes = computed(() => cuentasPorPagar.value.slice(0, 5));

function normalizarLista(response) {
  return response?.results ?? response ?? [];
}

async function cargarTodasLasPaginas(fetcher, params = {}) {
  const items = [];
  let page = 1;
  let hasNext = true;

  while (hasNext) {
    const response = await fetcher({ ...params, page });
    const results = normalizarLista(response);

    items.push(...results);
    hasNext = Boolean(response?.next);
    page += 1;
  }

  return items;
}

function numero(value) {
  return Number(value || 0);
}

function formatoCRC(value) {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
    maximumFractionDigits: 0,
  }).format(numero(value));
}

function formatoNumero(value) {
  return new Intl.NumberFormat("es-CR", {
    maximumFractionDigits: 2,
  }).format(numero(value));
}

function formatoFecha(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("es-CR");
}

function esMismaFecha(value, date) {
  const current = new Date(value);

  return (
    current.getFullYear() === date.getFullYear() &&
    current.getMonth() === date.getMonth() &&
    current.getDate() === date.getDate()
  );
}

function esMismoMes(value, year, month) {
  const date = new Date(value);
  return date.getFullYear() === year && date.getMonth() === month;
}

function nombreMes(year, month) {
  return new Date(year, month, 1).toLocaleDateString("es-CR", {
    month: "short",
  });
}

function serieMensual(items, dateKey, valueKey) {
  const months = [];

  for (let offset = 5; offset >= 0; offset -= 1) {
    const date = new Date(anioActual, mesActual - offset, 1);
    months.push({
      year: date.getFullYear(),
      month: date.getMonth(),
      label: nombreMes(date.getFullYear(), date.getMonth()),
      value: 0,
    });
  }

  items.forEach((item) => {
    const date = new Date(item[dateKey]);
    const month = months.find(
      (entry) =>
        entry.year === date.getFullYear() && entry.month === date.getMonth()
    );

    if (month) {
      month.value += numero(item[valueKey]);
    }
  });

  return months;
}

function porcentajeBarra(value, items) {
  const max = Math.max(...items.map((item) => numero(item.value)), 0);
  if (!max) return 0;
  return Math.max((numero(value) / max) * 100, 4);
}

function mostrarError(message) {
  snackbarText.value = message;
  snackbar.value = true;
}

async function cargarDashboard() {
  loading.value = true;

  try {
    const [
      ventasData,
      comprasData,
      productosData,
      clientesData,
      proveedoresData,
      cuentasPorCobrarData,
      cuentasPorPagarData,
    ] = await Promise.all([
      cargarTodasLasPaginas(getVentas, { ordering: "-fecha" }),
      cargarTodasLasPaginas(getCompras, { ordering: "-fecha" }),
      cargarTodasLasPaginas(getProductos, { ordering: "nombre" }),
      cargarTodasLasPaginas(getClientes, { ordering: "nombre" }),
      cargarTodasLasPaginas(getProveedores, { ordering: "nombre" }),
      cargarTodasLasPaginas(getCuentasPorCobrar, {
        estado: "PENDIENTE",
        ordering: "fecha_vencimiento",
      }),
      cargarTodasLasPaginas(getCuentasPorPagar, {
        estado: "PENDIENTE",
        ordering: "fecha_vencimiento",
      }),
    ]);

    ventas.value = ventasData;
    compras.value = comprasData;
    productos.value = productosData;
    clientes.value = clientesData;
    proveedores.value = proveedoresData;
    cuentasPorCobrar.value = cuentasPorCobrarData;
    cuentasPorPagar.value = cuentasPorPagarData;
  } catch (error) {
    console.error(error.response?.data || error);
    mostrarError("No se pudo cargar la información del dashboard.");
  } finally {
    loading.value = false;
  }
}

onMounted(cargarDashboard);
</script>

<template>
  <section class="dashboard-view">
    <div class="d-flex align-center mb-4">
      <div>
        <h1 class="text-h5 font-weight-bold mb-1">Dashboard</h1>
        <p class="text-body-2 text-medium-emphasis mb-0">
          Resumen operativo de ventas, compras, inventario y cuentas pendientes.
        </p>
      </div>

      <v-spacer />

      <v-btn
        color="primary"
        variant="tonal"
        prepend-icon="mdi-refresh"
        :loading="loading"
        @click="cargarDashboard"
      >
        Actualizar
      </v-btn>
    </div>

    <v-row>
      <v-col
        v-for="kpi in kpis"
        :key="kpi.title"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card class="dashboard-card kpi-card" :loading="loading">
          <v-card-text class="d-flex align-center">
            <v-avatar :color="kpi.color" variant="tonal" rounded="0" class="mr-3">
              <v-icon :icon="kpi.icon" />
            </v-avatar>

            <div>
              <div class="text-caption text-medium-emphasis">{{ kpi.title }}</div>
              <div class="text-h6 font-weight-bold">{{ kpi.value }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-1">
      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">Ventas por mes</v-card-title>
          <v-card-text>
            <div class="bar-chart">
              <div v-for="item in ventasPorMes" :key="item.label" class="bar-row">
                <span class="bar-label">{{ item.label }}</span>
                <div class="bar-track">
                  <div
                    class="bar-fill sales"
                    :style="{ width: `${porcentajeBarra(item.value, ventasPorMes)}%` }"
                  />
                </div>
                <span class="bar-value">{{ formatoCRC(item.value) }}</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">Compras por mes</v-card-title>
          <v-card-text>
            <div class="bar-chart">
              <div v-for="item in comprasPorMes" :key="item.label" class="bar-row">
                <span class="bar-label">{{ item.label }}</span>
                <div class="bar-track">
                  <div
                    class="bar-fill purchases"
                    :style="{ width: `${porcentajeBarra(item.value, comprasPorMes)}%` }"
                  />
                </div>
                <span class="bar-value">{{ formatoCRC(item.value) }}</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">Productos más vendidos</v-card-title>
          <v-card-text>
            <div class="bar-chart">
              <div
                v-for="item in productosMasVendidos"
                :key="item.label"
                class="bar-row"
              >
                <span class="bar-label product-label">{{ item.label }}</span>
                <div class="bar-track">
                  <div
                    class="bar-fill products"
                    :style="{
                      width: `${porcentajeBarra(item.value, productosMasVendidos)}%`,
                    }"
                  />
                </div>
                <span class="bar-value">{{ formatoNumero(item.value) }}</span>
              </div>
              <v-empty-state
                v-if="!productosMasVendidos.length"
                icon="mdi-package-variant"
                title="Sin ventas registradas"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">Productos con menor stock</v-card-title>
          <v-card-text>
            <v-list density="compact" lines="two">
              <v-list-item
                v-for="item in productosMenorStock"
                :key="item.label"
                :title="item.label"
                :subtitle="item.meta"
              >
                <template #prepend>
                  <v-icon color="warning" icon="mdi-package-variant" />
                </template>
                <template #append>
                  <v-chip size="small" variant="tonal" color="warning">
                    {{ formatoNumero(item.value) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-1">
      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">Últimas ventas</v-card-title>
          <v-table density="compact">
            <thead>
              <tr>
                <th>Comprobante</th>
                <th>Cliente</th>
                <th>Fecha</th>
                <th class="text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="venta in ultimasVentas" :key="venta.id">
                <td>{{ venta.numero_comprobante }}</td>
                <td>{{ venta.cliente_nombre || "Consumidor final" }}</td>
                <td>{{ formatoFecha(venta.fecha) }}</td>
                <td class="text-right">{{ formatoCRC(venta.total) }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">Últimas compras</v-card-title>
          <v-table density="compact">
            <thead>
              <tr>
                <th>Factura</th>
                <th>Proveedor</th>
                <th>Fecha</th>
                <th class="text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="compra in ultimasCompras" :key="compra.id">
                <td>{{ compra.numero_factura }}</td>
                <td>{{ compra.proveedor_nombre }}</td>
                <td>{{ formatoFecha(compra.fecha) }}</td>
                <td class="text-right">{{ formatoCRC(compra.total) }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">
            Cuentas por cobrar pendientes
          </v-card-title>
          <v-table density="compact">
            <thead>
              <tr>
                <th>Venta</th>
                <th>Cliente</th>
                <th>Vence</th>
                <th class="text-right">Saldo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cuenta in cuentasPorCobrarPendientes" :key="cuenta.id">
                <td>{{ cuenta.venta_numero }}</td>
                <td>{{ cuenta.cliente_nombre }}</td>
                <td>{{ formatoFecha(cuenta.fecha_vencimiento) }}</td>
                <td class="text-right">{{ formatoCRC(cuenta.saldo) }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card class="dashboard-card" :loading="loading">
          <v-card-title class="text-subtitle-1">
            Cuentas por pagar pendientes
          </v-card-title>
          <v-table density="compact">
            <thead>
              <tr>
                <th>Compra</th>
                <th>Proveedor</th>
                <th>Vence</th>
                <th class="text-right">Saldo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cuenta in cuentasPorPagarPendientes" :key="cuenta.id">
                <td>{{ cuenta.compra_numero }}</td>
                <td>{{ cuenta.proveedor_nombre }}</td>
                <td>{{ formatoFecha(cuenta.fecha_vencimiento) }}</td>
                <td class="text-right">{{ formatoCRC(cuenta.saldo) }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snackbar" color="error" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>

<style scoped>
.dashboard-view {
  min-width: 0;
}

.dashboard-card {
  border-radius: 8px;
  height: 100%;
}

.kpi-card :deep(.v-card-text) {
  min-height: 88px;
}

.bar-chart {
  display: grid;
  gap: 12px;
}

.bar-row {
  align-items: center;
  display: grid;
  gap: 10px;
  grid-template-columns: 68px minmax(80px, 1fr) 96px;
}

.bar-label {
  color: rgba(var(--v-theme-on-surface), 0.72);
  font-size: 0.82rem;
  text-transform: capitalize;
}

.product-label {
  overflow: hidden;
  text-overflow: ellipsis;
  text-transform: none;
  white-space: nowrap;
}

.bar-track {
  background: rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
}

.bar-fill {
  border-radius: inherit;
  height: 100%;
}

.bar-fill.sales {
  background: rgb(var(--v-theme-success));
}

.bar-fill.purchases {
  background: rgb(var(--v-theme-warning));
}

.bar-fill.products {
  background: rgb(var(--v-theme-primary));
}

.bar-value {
  font-size: 0.78rem;
  font-weight: 600;
  text-align: right;
}

@media (max-width: 600px) {
  .bar-row {
    grid-template-columns: 56px minmax(70px, 1fr) 76px;
  }

  .bar-value {
    font-size: 0.72rem;
  }
}
</style>
