import { reactive, watch } from "vue";

export function usePersistentFilters(key, defaults) {
  const saved = JSON.parse(localStorage.getItem(key) || "{}");
  const filters = reactive({
    ...defaults,
    ...saved,
  });

  watch(
    filters,
    (value) => {
      localStorage.setItem(key, JSON.stringify(value));
    },
    { deep: true }
  );

  function resetFilters() {
    Object.assign(filters, defaults);
  }

  return {
    filters,
    resetFilters,
  };
}
