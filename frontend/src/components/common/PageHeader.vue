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
  <v-row class="page-header mb-4" align="center">
    <v-col cols="12" sm="">
      <h1 class="text-h5 font-weight-bold">{{ title }}</h1>
      <p class="text-body-2 text-medium-emphasis mb-0">{{ subtitle }}</p>
    </v-col>

    <v-col v-if="buttonText" cols="12" sm="auto">
      <v-btn
        class="page-header__button"
        color="primary"
        :prepend-icon="buttonIcon"
        @click="emit('click')"
      >
        {{ buttonText }}
      </v-btn>
    </v-col>
  </v-row>
</template>

<style scoped>
.page-header__button {
  width: 100%;
}

@media (min-width: 600px) {
  .page-header__button {
    width: auto;
  }
}
</style>
