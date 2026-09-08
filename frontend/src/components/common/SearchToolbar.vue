<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const model = defineModel();

const props = defineProps({
  label: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["search"]);
const { t } = useI18n();
const effectiveLabel = computed(() => props.label || t("common.search"));
</script>

<template>
  <v-card-title>
    <v-row align="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-text-field
          v-model="model"
          :label="effectiveLabel"
          prepend-inner-icon="mdi-magnify"
          density="compact"
          variant="outlined"
          hide-details
          clearable
          @keyup.enter="emit('search')"
          @click:clear="emit('search')"
        />
      </v-col>

      <v-col cols="12" sm="auto">
        <v-btn class="search-button" variant="tonal" @click="emit('search')">
          {{ $t("common.search") }}
        </v-btn>
      </v-col>
    </v-row>
  </v-card-title>
</template>

<style scoped>
.search-button {
  width: 100%;
}

@media (min-width: 600px) {
  .search-button {
    width: auto;
  }
}
</style>
