<script setup>
import { storeToRefs } from "pinia";
import { useUiStore } from "@/stores/ui";

const uiStore = useUiStore();
const { isLoading } = storeToRefs(uiStore);
</script>

<template>
  <v-fade-transition>
    <div v-if="isLoading" class="global-loading">
      <v-progress-linear color="primary" indeterminate height="3" />
    </div>
  </v-fade-transition>
</template>

<style scoped>
.global-loading {
  left: 0;
  pointer-events: none;
  position: fixed;
  right: 0;
  top: 0;
  z-index: 3000;
}
</style>
