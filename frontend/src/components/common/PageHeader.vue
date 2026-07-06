<script setup>
defineProps({
  title: String,
  subtitle: String,
  buttonText: String,
  buttonIcon: {
    type: String,
    default: "mdi-plus",
  },
});

const emit = defineEmits(["click"]);

</script>

<template>
  <v-row class="mb-4" align="center">
    <v-col>
      <h1 class="text-h5 font-weight-bold">{{ title }}</h1>
      <p class="text-body-2 text-medium-emphasis">{{ subtitle }}</p>
    </v-col>

    <v-col v-if="buttonText" cols="auto">
      <v-btn color="primary" :prepend-icon="buttonIcon" @click="emit('click')">
        {{ buttonText }}
      </v-btn>
    </v-col>
  </v-row>
</template>