<script setup>
const model = defineModel();

defineProps({
  label: {
    type: String,
    default: "Buscar",
  },
});

const emit = defineEmits(["search"]);
</script>

<template>
  <v-card-title>
    <v-row align="center">
      <v-col cols="12" md="4">
        <v-text-field
          v-model="model"
          :label="label"
          prepend-inner-icon="mdi-magnify"
          density="compact"
          variant="outlined"
          hide-details
          clearable
          @keyup.enter="emit('search')"
          @click:clear="emit('search')"
        />
      </v-col>

      <v-col cols="auto">
        <v-btn variant="tonal" @click="emit('search')">
          Buscar
        </v-btn>
      </v-col>
    </v-row>
  </v-card-title>
</template>