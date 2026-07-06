<script setup>

import { computed, reactive, ref, watch } from "vue";

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
  editing: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "update:modelValue",
  "save",
]);

const formRef = ref(null);

const rules = {
  required: (value) =>
    !!value || "Este campo es obligatorio",

  positive: (value) =>
    Number(value) > 0 || "Debe ser mayor que cero",

  salePrice: (value) =>
    Number(value) >= Number(form.precio_compra) ||
    "El precio de venta debe ser mayor o igual al precio de compra",
};

const dialog = computed({
  get: () => props.modelValue,
  set: value => emit("update:modelValue", value),
});

const form = reactive({
  codigo: "",
  nombre: "",
  descripcion: "",
  categoria: null,
  precio_compra: 0,
  precio_venta: 0,
  estado: true,
});

watch(
  () => props.producto,
  (nuevo) => {
    Object.assign(form, {
      codigo: nuevo?.codigo ?? "",
      nombre: nuevo?.nombre ?? "",
      descripcion: nuevo?.descripcion ?? "",
      categoria: nuevo?.categoria ?? null,
      precio_compra: nuevo?.precio_compra ?? 0,
      precio_venta: nuevo?.precio_venta ?? 0,
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
  <v-dialog
    v-model="dialog"
    max-width="700"
  >
    <v-card>

      <v-card-title>
        {{ editing ? "Editar producto" : "Nuevo producto" }}
      </v-card-title>

      <v-divider />

      <v-card-text>
        
        <v-form ref="formRef"></v-form>
        
        <v-row>
          
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.codigo"
              label="Código"
              variant="outlined"
              :rules="[rules.required]"
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.nombre"
              label="Nombre"
              variant="outlined"
              :rules="[rules.required]"
            />
          </v-col>

          <v-col cols="12">
            <v-textarea
              v-model="form.descripcion"
              label="Descripción"
              rows="3"
              variant="outlined"
              :rules="[rules.required]"
            />
          </v-col>

          <v-col cols="12">
            <v-select
              v-model="form.categoria"
              :items="categorias"
              item-title="nombre"
              item-value="id"
              label="Categoría"
              variant="outlined"
              :rules="[rules.required]"
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="form.precio_compra"
              label="Precio Compra"
              type="number"
              variant="outlined"
              prefix="₡"
              :rules="[rules.required]"
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="form.precio_venta"
              label="Precio Venta"
              type="number"
              variant="outlined"
              prefix="₡"
              :rules="[
                rules.required,
                rules.positive,
                rules.salePrice
              ]"
            />
          </v-col>

          <v-col cols="12">
            <v-switch
              v-model="form.estado"
              label="Producto activo"
              color="primary"
            />
          </v-col>

        </v-row>
        
    </v-card-text>

      <v-divider />

      <v-card-actions>

        <v-spacer />

        <v-btn
          variant="text"
          @click="dialog = false"
        >
          Cancelar
        </v-btn>

        <v-btn
          color="primary"
          @click="guardar"
        >
          Guardar
        </v-btn>

      </v-card-actions>

    </v-card>
  </v-dialog>
</template>