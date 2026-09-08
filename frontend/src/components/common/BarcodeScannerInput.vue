<script setup>
import { ref } from "vue";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps({
  label: {
    type: String,
    default: "",
  },
  loading: Boolean,
  autofocus: Boolean,
});

const emit = defineEmits(["scan"]);
const { t } = useI18n();
const effectiveLabel = computed(() => props.label || t("common.scanBarcode"));
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
    :label="effectiveLabel"
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
