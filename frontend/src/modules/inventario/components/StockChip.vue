<script setup>
const props = defineProps({
  stock: {
    type: Number,
    default: 0,
  },
});

function getColor(stock) {
  if (stock <= 0) return "red";
  if (stock <= 10) return "orange";
  return "green";
}

function getIcon(stock) {
  if (stock <= 0) return "mdi-close-circle";
  if (stock <= 10) return "mdi-alert-circle";
  return "mdi-check-circle";
}

function getText(stock) {
  if (stock <= 0) return "Sin stock";
  if (stock <= 10) return "Stock bajo";
  return "Disponible";
}
</script>

<template>
  <v-tooltip :text="getText(stock)">
    <template #activator="{ props }">
      <v-chip
        v-bind="props"
        :color="getColor(stock)"
        :prepend-icon="getIcon(stock)"
        variant="tonal"
        size="small"
      >
        {{ stock }}
      </v-chip>
    </template>
  </v-tooltip>
</template>