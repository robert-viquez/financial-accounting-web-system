<script setup>
import { computed } from "vue";
import { useDisplay } from "vuetify";
import { useI18n } from "vue-i18n";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: "",
  },
  maxWidth: {
    type: String,
    default: "700",
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "save"]);
const display = useDisplay();
const { t } = useI18n();
const effectiveTitle = computed(() => props.title || t("common.form"));
const isPhone = computed(() => display.xs.value);

const dialogMaxWidth = computed(() =>
  display.smAndDown.value ? undefined : props.maxWidth
);

function close() {
  emit("update:modelValue", false);
}

function save() {
  emit("save");
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    :fullscreen="isPhone"
    :max-width="dialogMaxWidth"
    scrollable
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card class="crud-dialog-card">
      <v-card-title class="d-flex align-center">
        <span class="dialog-title">{{ effectiveTitle }}</span>

        <v-spacer />

        <v-btn
          icon="mdi-close"
          variant="text"
          size="small"
          @click="close"
        />
      </v-card-title>

      <v-divider />

      <v-card-text>
        <slot />
      </v-card-text>

      <v-divider />

      <v-card-actions class="dialog-actions">
        <v-spacer class="d-none d-sm-flex" />

        <v-btn variant="text" @click="close">
          {{ $t("common.cancel") }}
        </v-btn>

        <v-btn color="primary" :loading="loading" @click="save">
          {{ $t("common.save") }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.crud-dialog-card {
  width: 100%;
}

.dialog-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-actions {
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 599px) {
  .dialog-actions :deep(.v-btn) {
    flex: 1 1 140px;
  }
}
</style>
