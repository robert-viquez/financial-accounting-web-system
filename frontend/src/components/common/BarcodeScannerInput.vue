<script setup>
import { ref } from "vue";

defineProps({
  label: {
    type: String,
    default: "Escanear código de barras",
  },
  loading: Boolean,
  autofocus: Boolean,
});

const emit = defineEmits(["scan"]);
const codigo = ref("");

function procesar() {
  const valor = codigo.value.trim();
  if (!valor) return;
  emit("scan", valor);
  codigo.value = "";
}
</script>

<template>
  <v-text-field
    v-model="codigo"
    :label="label"
    prepend-inner-icon="mdi-barcode-scan"
    append-inner-icon="mdi-keyboard-return"
    variant="outlined"
    density="comfortable"
    :loading="loading"
    :autofocus="autofocus"
    hide-details
    autocomplete="off"
    @keyup.enter="procesar"
    @click:append-inner="procesar"
  />
</template>
