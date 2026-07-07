import { computed, reactive } from "vue";

export function useServerTable(defaults = {}) {
  const options = reactive({
    page: defaults.page || 1,
    itemsPerPage: defaults.itemsPerPage || 10,
    sortBy: defaults.sortBy || [],
  });

  const serverParams = computed(() => {
    const sort = options.sortBy?.[0];
    const params = {
      page: options.page,
      page_size: options.itemsPerPage,
    };

    if (sort?.key) {
      params.ordering = sort.order === "desc" ? `-${sort.key}` : sort.key;
    } else if (defaults.ordering) {
      params.ordering = defaults.ordering;
    }

    return params;
  });

  function updateOptions(value) {
    options.page = value.page;
    options.itemsPerPage = value.itemsPerPage;
    options.sortBy = value.sortBy || [];
  }

  return {
    options,
    serverParams,
    updateOptions,
  };
}
