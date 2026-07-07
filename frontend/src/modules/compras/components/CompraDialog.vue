<script setup>
import { computed, reactive, ref, watch } from "vue";
import BaseCrudDialog from "@/components/common/BaseCrudDialog.vue";

const props = defineProps({
  modelValue: Boolean,
  proveedores: {
    type: Array,
    default: () => [],
  },
  productos: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
});

const emit = defineEmits(["update:modelValue", "save"]);

const formRef = ref(null);

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const form = reactive({
  proveedor: null,
  numero_factura: "",
  tipo_compra: "CONTADO",
  observaciones: "",
  detalles: [],
});

const rules = {
  required: (value) => !!value || "Este campo es obligatorio",
  positive: (value) => Number(value) > 0 || "Debe ser mayor que cero",
};

const total = computed(() =>
  form.detalles.reduce((sum, item) => {
    return sum + Number(item.cantidad || 0) * Number(item.costo_unitario || 0);
  }, 0)
);

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) resetForm();
  }
);

function resetForm() {
  form.proveedor = null;
  form.numero_factura = "";
  form.tipo_compra = "CONTADO";
  form.observaciones = "";
  form.detalles = [
    {
      producto: null,
      cantidad: 1,
      costo_unitario: 0,
    },
  ];
}

function agregarDetalle() {
  form.detalles.push({
    producto: null,
    cantidad: 1,
    costo_unitario: 0,
  });
}

function eliminarDetalle(index) {
  if (form.detalles.length === 1) return;
  form.detalles.splice(index, 1);
}

function getSubtotal(detalle) {
  return Number(detalle.cantidad || 0) * Number(detalle.costo_unitario || 0);
}

function formatoCRC(valor) {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
  }).format(Number(valor || 0));
}

async function guardar() {
  const { valid } = await formRef.value.validate();

  if (!valid) return;

  const detallesValidos = form.detalles.every(
    (detalle) =>
      detalle.producto &&
      Number(detalle.cantidad) > 0 &&
      Number(detalle.costo_unitario) > 0
  );

  if (!detallesValidos) return;

  emit("save", {
    proveedor: form.proveedor,
    numero_factura: form.numero_factura,
    tipo_compra: form.tipo_compra,
    observaciones: form.observaciones,
    detalles: form.detalles.map((detalle) => ({
      producto: detalle.producto,
      cantidad: Number(detalle.cantidad).toFixed(2),
      costo_unitario: Number(detalle.costo_unitario).toFixed(2),
    })),
  });
}
</script>

<template>
  <BaseCrudDialog
    v-model="dialog"
    title="Nueva compra"
    max-width="1000"
    :loading="loading"
    @save="guardar"
  >
    <v-form ref="formRef">
      <v-row>
        <v-col cols="12" md="4">
          <v-select
            v-model="form.proveedor"
            :items="proveedores"
            item-title="nombre"
            item-value="id"
            label="Proveedor"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" md="4">
          <v-text-field
            v-model="form.numero_factura"
            label="Número de factura"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" md="4">
          <v-select
            v-model="form.tipo_compra"
            :items="[
              { title: 'Contado', value: 'CONTADO' },
              { title: 'Crédito', value: 'CREDITO' },
            ]"
            label="Tipo de compra"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12">
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
        <h3 class="text-subtitle-1 font-weight-bold">Detalle de compra</h3>

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
            <th style="width: 140px">Cantidad</th>
            <th style="width: 180px">Costo unitario</th>
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
              />
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
                v-model.number="detalle.costo_unitario"
                type="number"
                variant="outlined"
                density="compact"
                prefix="₡"
                hide-details
                :rules="[rules.required, rules.positive]"
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
        <h2 class="text-h6">
          Total: {{ formatoCRC(total) }}
        </h2>
      </div>
    </v-form>
  </BaseCrudDialog>
</template>