<script setup>
import { computed, reactive, ref, watch } from "vue";
import BaseCrudDialog from "@/components/common/BaseCrudDialog.vue";

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
});

const emit = defineEmits(["update:modelValue", "save", "validation-error"]);

const formRef = ref(null);
const errorMessage = ref("");

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
  form.cliente = null;
  form.medio_pago = null;
  form.numero_comprobante = "";
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
  return props.productos.find((producto) => producto.id === productoId);
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
    numero_comprobante: form.numero_comprobante,
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
        v-if="errorMessage"
        class="mb-4"
        type="error"
        variant="tonal"
        density="compact"
      >
        {{ errorMessage }}
      </v-alert>

      <v-row>
        <v-col cols="12" md="3">
          <v-select
            v-model="form.cliente"
            :items="clientes"
            item-title="nombre"
            item-value="id"
            label="Cliente"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" md="3">
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

        <v-col cols="12" md="3">
          <v-text-field
            v-model="form.numero_comprobante"
            label="Número de comprobante"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" md="3">
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

        <v-col cols="12" md="3">
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

        <v-col cols="12" md="9">
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

      <div class="d-flex align-center mb-3">
        <h3 class="text-subtitle-1 font-weight-bold">Detalle de venta</h3>

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

      <v-table>
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
                :items="productos"
                item-title="nombre"
                item-value="id"
                label="Producto"
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

      <div class="d-flex justify-end">
        <h2 class="text-h6">Total: {{ formatoCRC(total) }}</h2>
      </div>
    </v-form>
  </BaseCrudDialog>
</template>
