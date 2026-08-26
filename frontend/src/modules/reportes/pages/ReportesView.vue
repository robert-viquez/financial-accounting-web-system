<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import { fetchAllPages } from "@/api/pagination";
import { getCompras } from "@/modules/compras/api/ComprasServices";
import {
  getCuentasPorCobrar,
  getCuentasPorPagar,
} from "@/modules/finanzas/api/finanzasService";
import { getProductos } from "@/modules/inventario/api/ProductosServices";
import { getVentas } from "@/modules/ventas/api/ventasService";
import { exportarReportes, getReporteContable } from "@/modules/contabilidad/api/contabilidadService";

const loading = ref(false);
const exporting = ref("");
const rows = ref([]);
const snackbar = ref(false);
const snackbarText = ref("");

const filters = reactive({
  reporte: "ventas",
  reportes: ["ventas"],
  desde: "",
  hasta: "",
});

const reportes = [
  { title: "Balance General", value: "balance_general" },
  { title: "Estado de Resultados", value: "estado_resultados" },
  { title: "Libro Diario", value: "libro_diario" },
  { title: "Libro Mayor", value: "libro_mayor" },
  { title: "Balance de Comprobación", value: "balance_comprobacion" },
  { title: "Inventario", value: "inventario" },
  { title: "Ventas", value: "ventas" },
  { title: "Compras", value: "compras" },
  { title: "CxC", value: "cxc" },
  { title: "CxP", value: "cxp" },
];

const headers = computed(() => {
  const map = {
    ventas: ["Fecha", "Comprobante", "Cliente", "Estado", "Total"],
    compras: ["Fecha", "Factura", "Proveedor", "Estado", "Total"],
    inventario: ["Código", "Producto", "Stock", "Costo", "Precio"],
    cxc: ["Venta", "Cliente", "Vence", "Estado", "Saldo"],
    cxp: ["Compra", "Proveedor", "Vence", "Estado", "Saldo"],
    libro_diario: ["Fecha", "Asiento", "Cuenta", "Descripción", "Debe", "Haber"],
    libro_mayor: ["Cuenta", "Debe", "Haber", "Saldo"],
    balance_general: ["Concepto", "Monto"],
    estado_resultados: ["Concepto", "Monto"],
    balance_comprobacion: ["Cuenta", "Debe", "Haber"],
  };

  return map[filters.reporte] || [];
});

const tituloReporte = computed(
  () => reportes.find((reporte) => reporte.value === filters.reporte)?.title
);

function numero(value) {
  return Number(value || 0);
}

function formatoCRC(value) {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
  }).format(numero(value));
}

function formatoFecha(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("es-CR");
}

function filtrarPorFecha(items, key) {
  return items.filter((item) => {
    const fecha = new Date(item[key]);
    const desde = filters.desde ? new Date(`${filters.desde}T00:00:00`) : null;
    const hasta = filters.hasta ? new Date(`${filters.hasta}T23:59:59`) : null;

    if (desde && fecha < desde) return false;
    if (hasta && fecha > hasta) return false;
    return true;
  });
}

async function cargarReporte() {
  if (!validarPeriodo()) return;
  loading.value = true;

  try {
    if (filters.reporte === "ventas") {
      const data = filtrarPorFecha(await fetchAllPages(getVentas, { ordering: "-fecha" }), "fecha");
      rows.value = data.map((venta) => [
        formatoFecha(venta.fecha),
        venta.numero_comprobante,
        venta.cliente_nombre || "Consumidor final",
        venta.estado,
        formatoCRC(venta.total),
      ]);
    } else if (filters.reporte === "compras") {
      const data = filtrarPorFecha(await fetchAllPages(getCompras, { ordering: "-fecha" }), "fecha");
      rows.value = data.map((compra) => [
        formatoFecha(compra.fecha),
        compra.numero_factura,
        compra.proveedor_nombre,
        compra.estado,
        formatoCRC(compra.total),
      ]);
    } else if (filters.reporte === "inventario") {
      const data = await fetchAllPages(getProductos, { ordering: "nombre" });
      rows.value = data.map((producto) => [
        producto.codigo,
        producto.nombre,
        producto.stock_actual,
        formatoCRC(producto.costo_promedio),
        formatoCRC(producto.precio_venta),
      ]);
    } else if (filters.reporte === "cxc") {
      const data = await fetchAllPages(getCuentasPorCobrar, { ordering: "fecha_vencimiento" });
      rows.value = data.map((cuenta) => [
        cuenta.venta_numero,
        cuenta.cliente_nombre,
        formatoFecha(cuenta.fecha_vencimiento),
        cuenta.estado,
        formatoCRC(cuenta.saldo),
      ]);
    } else if (filters.reporte === "cxp") {
      const data = await fetchAllPages(getCuentasPorPagar, { ordering: "fecha_vencimiento" });
      rows.value = data.map((cuenta) => [
        cuenta.compra_numero,
        cuenta.proveedor_nombre,
        formatoFecha(cuenta.fecha_vencimiento),
        cuenta.estado,
        formatoCRC(cuenta.saldo),
      ]);
    } else {
      await cargarReporteContable();
    }
  } catch (error) {
    snackbarText.value = "No se pudo generar el reporte.";
    snackbar.value = true;
  } finally {
    loading.value = false;
  }
}

async function cargarReporteContable() {
  const endpoint = {
    libro_diario: "libro-diario",
    libro_mayor: "libro-mayor",
    balance_general: "balance-general",
    estado_resultados: "estado-resultados",
    balance_comprobacion: "balance-comprobacion",
  };
  const data = await getReporteContable(endpoint[filters.reporte], {
    desde: filters.desde || undefined,
    hasta: filters.hasta || undefined,
  });

  if (filters.reporte === "libro_diario") {
    rows.value = data.flatMap((asiento) =>
      asiento.detalles.map((detalle) => [
        formatoFecha(asiento.fecha),
        asiento.numero,
        `${detalle.cuenta_codigo} - ${detalle.cuenta_nombre}`,
        detalle.descripcion || asiento.descripcion,
        formatoCRC(detalle.debe),
        formatoCRC(detalle.haber),
      ])
    );
  } else if (["libro_mayor", "balance_comprobacion"].includes(filters.reporte)) {
    rows.value = data.map((fila) => [
      `${fila.cuenta__codigo} - ${fila.cuenta__nombre}`,
      formatoCRC(fila.debe),
      formatoCRC(fila.haber),
      ...(filters.reporte === "libro_mayor" ? [formatoCRC(fila.saldo)] : []),
    ]);
  } else {
    rows.value = data.map((fila) => [fila.concepto, formatoCRC(fila.monto)]);
  }
}

function descargarArchivo(nombre, blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nombre;
  link.click();
  URL.revokeObjectURL(url);
}

function validarPeriodo() {
  if (filters.desde && filters.hasta && filters.desde > filters.hasta) {
    snackbarText.value = "La fecha inicial no puede ser posterior a la fecha final.";
    snackbar.value = true;
    return false;
  }
  return true;
}

function seleccionarTodos() {
  filters.reportes = filters.reportes.length === reportes.length
    ? []
    : reportes.map(({ value }) => value);
}

async function exportar(formato) {
  if (!validarPeriodo()) return;
  if (!filters.reportes.length) {
    snackbarText.value = "Seleccione al menos un reporte para exportar.";
    snackbar.value = true;
    return;
  }
  exporting.value = formato;
  try {
    const response = await exportarReportes(formato, {
      reportes: filters.reportes,
      desde: filters.desde || null,
      hasta: filters.hasta || null,
    });
    const disposition = response.headers["content-disposition"] || "";
    const match = disposition.match(/filename="?([^";]+)"?/);
    const fallback = `QuesoLosSantos_Reportes_${new Date().toISOString().slice(0, 10)}.${formato}`;
    descargarArchivo(match?.[1] || fallback, response.data);
  } catch (error) {
    console.error(error);
    snackbarText.value = "No se pudo generar el archivo. Revise la selección e inténtelo de nuevo.";
    snackbar.value = true;
  } finally {
    exporting.value = "";
  }
}

onMounted(cargarReporte);
</script>

<template>
  <section>
    <PageHeader
      title="Reportes"
      subtitle="Generación de reportes operativos y contables con filtros."
    />

    <v-card class="mb-4 no-print">
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="filters.desde"
              label="Desde"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="filters.hasta"
              label="Hasta"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="4" md="auto" class="d-flex align-center">
            <v-btn block color="primary" variant="tonal" :loading="loading" @click="cargarReporte">
              Filtrar
            </v-btn>
          </v-col>
        </v-row>
        <v-divider class="my-4" />
        <div class="d-flex flex-wrap align-center ga-2 mb-2">
          <span class="text-subtitle-2">Reportes para exportar</span>
          <v-btn size="small" variant="text" @click="seleccionarTodos">
            {{ filters.reportes.length === reportes.length ? "Quitar todos" : "Seleccionar todos" }}
          </v-btn>
        </div>
        <v-chip-group v-model="filters.reportes" column multiple selected-class="text-primary">
          <v-chip v-for="reporte in reportes" :key="reporte.value" :value="reporte.value" filter variant="outlined">
            {{ reporte.title }}
          </v-chip>
        </v-chip-group>
        <div class="d-flex flex-wrap ga-2 mt-4">
          <v-btn color="red-darken-2" variant="tonal" prepend-icon="mdi-file-pdf-box" :loading="exporting === 'pdf'" :disabled="Boolean(exporting)" @click="exportar('pdf')">
            Descargar PDF
          </v-btn>
          <v-btn color="green-darken-2" variant="tonal" prepend-icon="mdi-file-excel" :loading="exporting === 'xlsx'" :disabled="Boolean(exporting)" @click="exportar('xlsx')">
            Descargar XLSX
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-card :loading="loading" class="report-card">
      <v-card-title>{{ tituloReporte }}</v-card-title>
      <v-table density="compact">
        <thead>
          <tr>
            <th v-for="header in headers" :key="header">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in rows" :key="index">
            <td v-for="(cell, cellIndex) in row" :key="cellIndex">
              {{ cell }}
            </td>
          </tr>
          <tr v-if="!loading && !rows.length">
            <td :colspan="headers.length" class="text-center text-medium-emphasis py-8">
              No hay movimientos para el período seleccionado.
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-snackbar v-model="snackbar" color="error" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>

<style scoped>
.report-card :deep(th) {
  font-weight: 700;
  white-space: nowrap;
}

.report-card :deep(td:nth-last-child(-n + 3)) {
  font-variant-numeric: tabular-nums;
}
</style>
