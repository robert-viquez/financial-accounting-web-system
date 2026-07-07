<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import PageHeader from "@/components/common/PageHeader.vue";
import { getCompras } from "@/modules/compras/api/ComprasServices";
import {
  getCuentasPorCobrar,
  getCuentasPorPagar,
} from "@/modules/finanzas/api/finanzasService";
import { getMovimientos } from "@/modules/inventario/api/MovimientosServices";
import { getProductos } from "@/modules/inventario/api/ProductosServices";
import { getVentas } from "@/modules/ventas/api/ventasService";

const loading = ref(false);
const rows = ref([]);
const snackbar = ref(false);
const snackbarText = ref("");

const filters = reactive({
  reporte: "ventas",
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
    libro_diario: ["Fecha", "Producto", "Tipo", "Cantidad", "Descripción"],
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

function normalizar(response) {
  return response.results ?? response;
}

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
  loading.value = true;

  try {
    if (filters.reporte === "ventas") {
      const data = filtrarPorFecha(normalizar(await getVentas({ ordering: "-fecha" })), "fecha");
      rows.value = data.map((venta) => [
        formatoFecha(venta.fecha),
        venta.numero_comprobante,
        venta.cliente_nombre || "Consumidor final",
        venta.estado,
        formatoCRC(venta.total),
      ]);
    } else if (filters.reporte === "compras") {
      const data = filtrarPorFecha(normalizar(await getCompras({ ordering: "-fecha" })), "fecha");
      rows.value = data.map((compra) => [
        formatoFecha(compra.fecha),
        compra.numero_factura,
        compra.proveedor_nombre,
        compra.estado,
        formatoCRC(compra.total),
      ]);
    } else if (filters.reporte === "inventario") {
      const data = normalizar(await getProductos({ ordering: "nombre" }));
      rows.value = data.map((producto) => [
        producto.codigo,
        producto.nombre,
        producto.stock_actual,
        formatoCRC(producto.costo_promedio),
        formatoCRC(producto.precio_venta),
      ]);
    } else if (filters.reporte === "cxc") {
      const data = normalizar(await getCuentasPorCobrar({ ordering: "fecha_vencimiento" }));
      rows.value = data.map((cuenta) => [
        cuenta.venta_numero,
        cuenta.cliente_nombre,
        formatoFecha(cuenta.fecha_vencimiento),
        cuenta.estado,
        formatoCRC(cuenta.saldo),
      ]);
    } else if (filters.reporte === "cxp") {
      const data = normalizar(await getCuentasPorPagar({ ordering: "fecha_vencimiento" }));
      rows.value = data.map((cuenta) => [
        cuenta.compra_numero,
        cuenta.proveedor_nombre,
        formatoFecha(cuenta.fecha_vencimiento),
        cuenta.estado,
        formatoCRC(cuenta.saldo),
      ]);
    } else if (filters.reporte === "libro_diario") {
      const data = filtrarPorFecha(normalizar(await getMovimientos({ ordering: "-fecha" })), "fecha");
      rows.value = data.map((movimiento) => [
        formatoFecha(movimiento.fecha),
        movimiento.producto_nombre,
        movimiento.tipo,
        movimiento.cantidad,
        movimiento.descripcion || "-",
      ]);
    } else {
      rows.value = generarReporteContableBasico(filters.reporte);
    }
  } catch (error) {
    snackbarText.value = "No se pudo generar el reporte.";
    snackbar.value = true;
  } finally {
    loading.value = false;
  }
}

function generarReporteContableBasico(tipo) {
  const plantillas = {
    balance_general: [
      ["Activos", formatoCRC(0)],
      ["Pasivos", formatoCRC(0)],
      ["Patrimonio", formatoCRC(0)],
    ],
    estado_resultados: [
      ["Ingresos", formatoCRC(0)],
      ["Costos", formatoCRC(0)],
      ["Utilidad neta", formatoCRC(0)],
    ],
    libro_mayor: [
      ["Caja", formatoCRC(0), formatoCRC(0), formatoCRC(0)],
      ["Inventario", formatoCRC(0), formatoCRC(0), formatoCRC(0)],
    ],
    balance_comprobacion: [
      ["Caja", formatoCRC(0), formatoCRC(0)],
      ["Ventas", formatoCRC(0), formatoCRC(0)],
    ],
  };

  return plantillas[tipo] || [];
}

function descargarArchivo(nombre, contenido, tipo) {
  const blob = new Blob([contenido], { type: tipo });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nombre;
  link.click();
  URL.revokeObjectURL(url);
}

function exportarExcel() {
  const table = generarTablaHtml();
  descargarArchivo(
    `${filters.reporte}.xls`,
    table,
    "application/vnd.ms-excel;charset=utf-8"
  );
}

function exportarPdf() {
  window.print();
}

function generarTablaHtml() {
  const head = headers.value.map((header) => `<th>${header}</th>`).join("");
  const body = rows.value
    .map((row) => `<tr>${row.map((cell) => `<td>${cell ?? ""}</td>`).join("")}</tr>`)
    .join("");

  return `
    <html>
      <head><meta charset="UTF-8" /></head>
      <body>
        <h1>${tituloReporte.value}</h1>
        <table border="1">
          <thead><tr>${head}</tr></thead>
          <tbody>${body}</tbody>
        </table>
      </body>
    </html>
  `;
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
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.reporte"
              :items="reportes"
              label="Reporte"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model="filters.desde"
              label="Desde"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-text-field
              v-model="filters.hasta"
              label="Hasta"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="4" md="auto">
            <v-btn block color="primary" variant="tonal" @click="cargarReporte">
              Generar
            </v-btn>
          </v-col>
          <v-col cols="12" sm="4" md="auto">
            <v-btn block variant="tonal" prepend-icon="mdi-file-pdf-box" @click="exportarPdf">
              PDF
            </v-btn>
          </v-col>
          <v-col cols="12" sm="4" md="auto">
            <v-btn block variant="tonal" prepend-icon="mdi-file-excel" @click="exportarExcel">
              Excel
            </v-btn>
          </v-col>
        </v-row>
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
        </tbody>
      </v-table>
    </v-card>

    <v-snackbar v-model="snackbar" color="error" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }

  .report-card {
    box-shadow: none !important;
  }
}
</style>
