<script setup>
import { computed, reactive, ref, watch } from "vue";
import BaseCrudDialog from "@/components/common/BaseCrudDialog.vue";
import BarcodeScannerInput from "@/components/common/BarcodeScannerInput.vue";
import { getProductoPorCodigo } from "@/modules/inventario/api/ProductosServices";

const props = defineProps({
  modelValue: Boolean,
  clientes: {
    type: Array,
    default: () => [],
  },
  mediosPago: {
    type: Array,
    default: () => [],
  },
  productos: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  lectorHabilitado: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["update:modelValue", "save", "validation-error"]);

const formRef = ref(null);
const errorMessage = ref("");
const scanning = ref(false);
const productosEscaneados = ref([]);
const catalogoProductos = computed(() => {
  const productos = [...props.productos];
  for (const producto of productosEscaneados.value) {
    if (!productos.some((item) => item.id === producto.id)) productos.push(producto);
  }
  return productos;
});

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const form = reactive({
  cliente: null,
  medio_pago: null,
  numero_comprobante: "",
  tipo_venta: "CONTADO",
  descuento: 0,
  observaciones: "",
  detalles: [],
});

const rules = {
  required: (value) => !!value || "Este campo es obligatorio",
  positive: (value) => Number(value) > 0 || "Debe ser mayor que cero",
  zeroOrPositive: (value) => Number(value) >= 0 || "No puede ser negativo",
};

const subtotalDetalles = computed(() =>
  form.detalles.reduce((sum, item) => sum + getSubtotal(item), 0)
);

const total = computed(
  () => subtotalDetalles.value - Number(form.descuento || 0)
);

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) resetForm();
  }
);

function resetForm() {
  errorMessage.value = "";
  form.cliente =
    props.clientes.find(
      (cliente) => cliente.nombre?.trim().toLowerCase() === "estimado cliente"
    )?.id ?? null;
  form.medio_pago =
    props.mediosPago.find(
      (medio) => medio.nombre?.trim().toLowerCase() === "efectivo"
    )?.id ?? props.mediosPago[0]?.id ?? null;
  form.tipo_venta = "CONTADO";
  form.descuento = 0;
  form.observaciones = "";
  form.detalles = [
    {
      producto: null,
      cantidad: 1,
      precio_unitario: 0,
      descuento: 0,
    },
  ];
  productosEscaneados.value = [];
}

function agregarDetalle() {
  form.detalles.push({
    producto: null,
    cantidad: 1,
    precio_unitario: 0,
    descuento: 0,
  });
}

function eliminarDetalle(index) {
  if (form.detalles.length === 1) return;
  form.detalles.splice(index, 1);
}

function productoSeleccionado(productoId) {
  return catalogoProductos.value.find((producto) => producto.id === productoId);
}

async function escanearProducto(codigo) {
  scanning.value = true;
  try {
    const producto = await getProductoPorCodigo(codigo);
    if (!productosEscaneados.value.some((item) => item.id === producto.id)) {
      productosEscaneados.value.push(producto);
    }
    const existente = form.detalles.find(
      (detalle) => detalle.producto === producto.id
    );
    if (existente) {
      existente.cantidad = Number(existente.cantidad || 0) + 1;
    } else {
      const vacio = form.detalles.find((detalle) => !detalle.producto);
      const detalle = vacio ?? {
        producto: null,
        cantidad: 1,
        precio_unitario: 0,
        descuento: 0,
      };
      detalle.producto = producto.id;
      detalle.cantidad = 1;
      detalle.precio_unitario = Number(producto.precio_venta || 0);
      if (!vacio) form.detalles.push(detalle);
    }
    errorMessage.value = "";
  } catch (error) {
    mostrarErrorValidacion(
      error.response?.data?.detail || `No se encontró el código ${codigo}.`
    );
  } finally {
    scanning.value = false;
  }
}

function stockDisponible(productoId) {
  return Number(productoSeleccionado(productoId)?.stock_actual || 0);
}

function stockSolicitado(productoId) {
  if (!productoId) return 0;

  return form.detalles
    .filter((detalle) => detalle.producto === productoId)
    .reduce((sum, detalle) => sum + Number(detalle.cantidad || 0), 0);
}

function stockExcedido(detalle) {
  if (!detalle.producto) return false;
  return stockSolicitado(detalle.producto) > stockDisponible(detalle.producto);
}

function setPrecioProducto(detalle) {
  const producto = productoSeleccionado(detalle.producto);
  detalle.precio_unitario = producto ? Number(producto.precio_venta || 0) : 0;
}

function getSubtotal(detalle) {
  return (
    Number(detalle.cantidad || 0) * Number(detalle.precio_unitario || 0) -
    Number(detalle.descuento || 0)
  );
}

function formatoCRC(valor) {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
  }).format(Number(valor || 0));
}

function mostrarErrorValidacion(mensaje) {
  errorMessage.value = mensaje;
  emit("validation-error", mensaje);
}

function validarDescuentos() {
  for (const detalle of form.detalles) {
    const bruto =
      Number(detalle.cantidad || 0) * Number(detalle.precio_unitario || 0);

    if (Number(detalle.descuento || 0) > bruto) {
      mostrarErrorValidacion(
        "El descuento de una línea no puede ser mayor que su subtotal bruto."
      );
      return false;
    }
  }

  if (Number(form.descuento || 0) > subtotalDetalles.value) {
    mostrarErrorValidacion(
      "El descuento general no puede ser mayor que el subtotal."
    );
    return false;
  }

  return true;
}

function validarStockDisponible() {
  const cantidadesPorProducto = new Map();

  for (const detalle of form.detalles) {
    if (!detalle.producto) continue;

    cantidadesPorProducto.set(
      detalle.producto,
      (cantidadesPorProducto.get(detalle.producto) || 0) +
        Number(detalle.cantidad || 0)
    );
  }

  for (const [productoId, cantidad] of cantidadesPorProducto.entries()) {
    const producto = productoSeleccionado(productoId);
    const disponible = Number(producto?.stock_actual || 0);

    if (cantidad > disponible) {
      mostrarErrorValidacion(
        `Stock insuficiente para ${producto?.nombre || "el producto"}. Disponible: ${disponible}. Solicitado: ${cantidad}.`
      );
      return false;
    }
  }

  return true;
}

async function guardar() {
  errorMessage.value = "";

  const { valid } = await formRef.value.validate();

  if (!valid) return;

  const detallesValidos = form.detalles.every(
    (detalle) =>
      detalle.producto &&
      Number(detalle.cantidad) > 0 &&
      Number(detalle.precio_unitario) > 0 &&
      Number(detalle.descuento || 0) >= 0
  );

  if (!detallesValidos) {
    mostrarErrorValidacion("Complete correctamente el detalle de la venta.");
    return;
  }

  if (!validarDescuentos()) return;
  if (!validarStockDisponible()) return;

  emit("save", {
    cliente: form.cliente,
    medio_pago: form.medio_pago,
    tipo_venta: form.tipo_venta,
    descuento: Number(form.descuento || 0).toFixed(2),
    observaciones: form.observaciones,
    detalles: form.detalles.map((detalle) => ({
      producto: detalle.producto,
      cantidad: Number(detalle.cantidad).toFixed(2),
      precio_unitario: Number(detalle.precio_unitario).toFixed(2),
      descuento: Number(detalle.descuento || 0).toFixed(2),
    })),
  });
}
</script>

<template>
  <BaseCrudDialog
    v-model="dialog"
    title="Nueva venta"
    max-width="1100"
    :loading="loading"
    @save="guardar"
  >
    <v-form ref="formRef">
      <v-alert
        class="mb-4"
        type="info"
        variant="tonal"
        density="compact"
        icon="mdi-information-outline"
      >
        El comprobante se asignará automáticamente al guardar la venta.
      </v-alert>
      <v-alert
        v-if="errorMessage"
        class="mb-4"
        type="error"
        variant="tonal"
        density="compact"
      >
        {{ errorMessage }}
      </v-alert>

      <v-row dense>
        <v-col cols="12" sm="6" lg="4">
          <v-select
            v-model="form.cliente"
            :items="clientes"
            item-title="nombre"
            item-value="id"
            label="Cliente (predeterminado: Estimado Cliente)"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" sm="6" lg="4">
          <v-select
            v-model="form.medio_pago"
            :items="mediosPago"
            item-title="nombre"
            item-value="id"
            label="Medio de pago"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" sm="6" lg="4">
          <v-select
            v-model="form.tipo_venta"
            :items="[
              { title: 'Contado', value: 'CONTADO' },
              { title: 'Crédito', value: 'CREDITO' },
            ]"
            label="Tipo de venta"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" sm="6" lg="4">
          <v-text-field
            v-model.number="form.descuento"
            label="Descuento general"
            type="number"
            variant="outlined"
            density="compact"
            prefix="₡"
            :rules="[rules.zeroOrPositive]"
          />
        </v-col>

        <v-col cols="12" lg="8">
          <v-textarea
            v-model="form.observaciones"
            label="Observaciones"
            variant="outlined"
            density="compact"
            rows="2"
          />
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <div v-if="lectorHabilitado" class="scanner-sale mb-4">
        <div>
          <strong>Agregar con lector</strong>
          <p class="text-caption text-medium-emphasis mb-0">
            Cada lectura agrega una unidad; vuelva a escanear para aumentar la cantidad.
          </p>
        </div>
        <BarcodeScannerInput
          label="Escanear producto"
          :loading="scanning"
          @scan="escanearProducto"
        />
      </div>

      <div class="sale-section-header">
        <div>
          <h3 class="text-subtitle-1 font-weight-bold">Productos de la venta</h3>
          <p class="text-caption text-medium-emphasis mb-0">
            Seleccione el producto; el precio se completa automáticamente.
          </p>
        </div>

        <v-spacer />

        <v-btn
          color="primary"
          variant="tonal"
          prepend-icon="mdi-plus"
          @click="agregarDetalle"
        >
          Agregar producto
        </v-btn>
      </div>

      <v-table class="sale-table">
        <thead>
          <tr>
            <th>Producto</th>
            <th style="width: 120px">Stock</th>
            <th style="width: 140px">Cantidad</th>
            <th style="width: 180px">Precio unitario</th>
            <th style="width: 160px">Descuento</th>
            <th style="width: 160px">Subtotal</th>
            <th style="width: 80px">Acción</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(detalle, index) in form.detalles" :key="index">
            <td>
              <v-select
                v-model="detalle.producto"
                :items="catalogoProductos"
                item-title="nombre"
                item-value="id"
                label="Buscar producto"
                variant="outlined"
                density="compact"
                hide-details
                :rules="[rules.required]"
                @update:model-value="setPrecioProducto(detalle)"
              />
            </td>

            <td>
              <v-chip
                v-if="detalle.producto"
                :color="stockExcedido(detalle) ? 'error' : 'success'"
                variant="tonal"
                size="small"
              >
                {{ stockDisponible(detalle.producto) }}
              </v-chip>
              <span v-else>-</span>
            </td>

            <td>
              <v-text-field
                v-model.number="detalle.cantidad"
                type="number"
                variant="outlined"
                density="compact"
                hide-details
                :rules="[rules.required, rules.positive]"
              />
            </td>

            <td>
              <v-text-field
                v-model.number="detalle.precio_unitario"
                type="number"
                variant="outlined"
                density="compact"
                prefix="₡"
                hide-details
                :rules="[rules.required, rules.positive]"
              />
            </td>

            <td>
              <v-text-field
                v-model.number="detalle.descuento"
                type="number"
                variant="outlined"
                density="compact"
                prefix="₡"
                hide-details
                :rules="[rules.zeroOrPositive]"
              />
            </td>

            <td>
              {{ formatoCRC(getSubtotal(detalle)) }}
            </td>

            <td>
              <v-btn
                icon="mdi-delete"
                variant="text"
                color="error"
                size="small"
                :disabled="form.detalles.length === 1"
                @click="eliminarDetalle(index)"
              />
            </td>
          </tr>
        </tbody>
      </v-table>

      <v-divider class="my-4" />

      <div class="sale-total" aria-live="polite">
        <span>Total a cobrar</span>
        <strong>{{ formatoCRC(total) }}</strong>
      </div>
    </v-form>
  </BaseCrudDialog>
</template>

<style scoped>
.sale-section-header {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  margin-bottom: 12px;
}

.sale-table :deep(th) {
  white-space: nowrap;
}

.scanner-sale {
  align-items: center;
  background: rgba(var(--v-theme-primary), 0.07);
  border: 1px solid rgba(var(--v-theme-primary), 0.22);
  border-radius: 12px;
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(220px, 1fr) minmax(280px, 1.4fr);
  padding: 16px;
}

.sale-table :deep(td) {
  padding: 8px 6px;
}

.sale-total {
  align-items: center;
  background: rgb(var(--v-theme-primary));
  border-radius: 12px;
  color: rgb(var(--v-theme-on-primary));
  display: flex;
  font-size: 1.05rem;
  gap: 24px;
  justify-content: flex-end;
  margin-left: auto;
  padding: 14px 20px;
  width: min(100%, 420px);
}

.sale-total strong {
  font-size: 1.45rem;
}

@media (max-width: 700px) {
  .scanner-sale {
    grid-template-columns: 1fr;
  }
  .sale-section-header {
    align-items: stretch;
    flex-direction: column;
  }

  .sale-section-header .v-btn {
    width: 100%;
  }

  .sale-total {
    justify-content: space-between;
  }
}
</style>
