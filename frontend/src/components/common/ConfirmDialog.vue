<script setup>
const model = defineModel();

defineProps({
  title: {
    type: String,
    default: "Confirmar acción",
  },
  message: {
    type: String,
    default: "¿Desea continuar?",
  },
});

const emit = defineEmits(["confirm"]);
</script>

<template>
  <v-dialog v-model="model" max-width="420">
    <v-card>
      <v-card-title>{{ title }}</v-card-title>

      <v-card-text>
        {{ message }}
      </v-card-text>

      <v-card-actions>
        <v-spacer />

        <v-btn variant="text" @click="model = false">
          Cancelar
        </v-btn>

        <v-btn color="error" @click="emit('confirm')">
          Confirmar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>