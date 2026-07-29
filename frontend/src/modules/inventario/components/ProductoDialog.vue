<script setup>
import { computed, reactive, ref, watch } from "vue";
import BaseCrudDialog from "@/components/common/BaseCrudDialog.vue";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  producto: {
    type: Object,
    default: () => ({}),
  },
  categorias: {
    type: Array,
    default: () => [],
  },
  unidades: {
    type: Array,
    default: () => [],
  },
  editing: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "save"]);

const formRef = ref(null);

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const title = computed(() =>
  props.editing ? "Editar producto" : "Nuevo producto"
);

const form = reactive({
  codigo_barras: "",
  nombre: "",
  descripcion: "",
  categoria: null,
  costo_promedio: 0,
  precio_venta: 0,
  stock_minimo: 0,
  unidad_medida: null,
  estado: true,
});

const rules = {
  required: (value) => !!value || "Este campo es obligatorio",
  positive: (value) => Number(value) > 0 || "Debe ser mayor que cero",
  zeroOrPositive: (value) => Number(value) >= 0 || "No puede ser negativo",
  salePrice: (value) =>
    Number(value) >= Number(form.costo_promedio) ||
    "El precio de venta debe ser mayor o igual al costo promedio",
};

watch(
  () => props.producto,
  (nuevo) => {
    Object.assign(form, {
      codigo_barras: nuevo?.codigo_barras ?? "",
      nombre: nuevo?.nombre ?? "",
      descripcion: nuevo?.descripcion ?? "",
      categoria: nuevo?.categoria ?? null,
      costo_promedio: nuevo?.costo_promedio ?? 0,
      precio_venta: nuevo?.precio_venta ?? 0,
      stock_minimo: nuevo?.stock_minimo ?? 0,
      unidad_medida:
        nuevo?.unidad_medida ??
        props.unidades.find((unidad) => unidad.codigo === "UND")?.id ??
        props.unidades[0]?.id ??
        null,
      estado: nuevo?.estado ?? true,
    });
  },
  {
    immediate: true,
    deep: true,
  }
);

async function guardar() {
  const { valid } = await formRef.value.validate();

  if (!valid) return;

  emit("save", {
    ...form,
  });
}
</script>

<template>
  <BaseCrudDialog
    v-model="dialog"
    :title="title"
    :loading="loading"
    @save="guardar"
  >
    <v-form ref="formRef">
      <v-row>
        <v-col cols="12">
          <v-alert type="info" variant="tonal" density="compact">
            El código interno se generará con el código de la categoría.
          </v-alert>
        </v-col>

        <v-col v-if="editing" cols="12" sm="6">
          <v-text-field
            :model-value="producto.codigo"
            label="Código interno generado"
            variant="outlined"
            density="compact"
            readonly
          />
        </v-col>

        <v-col cols="12" sm="6">
          <v-text-field
            v-model="form.nombre"
            label="Nombre"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" sm="6">
          <v-text-field
            v-model="form.codigo_barras"
            label="Código de barras"
            hint="Escanee ahora o déjelo vacío para usar el código interno."
            persistent-hint
            prepend-inner-icon="mdi-barcode"
            variant="outlined"
            density="compact"
            autocomplete="off"
          />
        </v-col>

        <v-col cols="12" sm="6">
          <v-textarea
            v-model="form.descripcion"
            label="Descripción"
            rows="3"
            variant="outlined"
            density="compact"
          />
        </v-col>

        <v-col cols="12" sm="6">
          <v-select
            v-model="form.categoria"
            :items="categorias"
            item-title="nombre"
            item-value="id"
            label="Categoría"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" sm="6">
          <v-select
            v-model="form.unidad_medida"
            :items="unidades.filter((unidad) => unidad.estado)"
            item-title="nombre"
            item-value="id"
            label="Unidad de medida"
            variant="outlined"
            density="compact"
            :rules="[rules.required]"
          />
        </v-col>

        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.costo_promedio"
            label="Costo promedio"
            type="number"
            variant="outlined"
            density="compact"
            prefix="₡"
            :rules="[rules.zeroOrPositive]"
          />
        </v-col>

        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.precio_venta"
            label="Precio venta"
            type="number"
            variant="outlined"
            density="compact"
            prefix="₡"
            :rules="[rules.required, rules.positive, rules.salePrice]"
          />
        </v-col>

        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.stock_minimo"
            label="Stock mínimo"
            type="number"
            variant="outlined"
            density="compact"
            :rules="[rules.zeroOrPositive]"
          />
        </v-col>

        <v-col cols="12">
          <v-switch
            v-model="form.estado"
            label="Producto activo"
            color="primary"
            hide-details
          />
        </v-col>
      </v-row>
    </v-form>
  </BaseCrudDialog>
</template>
