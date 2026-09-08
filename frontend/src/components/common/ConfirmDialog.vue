<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const model = defineModel();

const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  message: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["confirm"]);
const { t } = useI18n();
const effectiveTitle = computed(() => props.title || t("common.confirmAction"));
const effectiveMessage = computed(() => props.message || t("common.continueQuestion"));
</script>

<template>
  <v-dialog v-model="model" max-width="420">
    <v-card>
      <v-card-title>{{ effectiveTitle }}</v-card-title>

      <v-card-text>
        {{ effectiveMessage }}
      </v-card-text>

      <v-card-actions>
        <v-spacer />

        <v-btn variant="text" @click="model = false">
          {{ $t("common.cancel") }}
        </v-btn>

        <v-btn color="error" @click="emit('confirm')">
          {{ $t("common.confirm") }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
