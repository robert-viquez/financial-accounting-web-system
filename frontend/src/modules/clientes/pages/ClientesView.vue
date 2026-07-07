<script setup>
import { onMounted, ref, watch } from "vue";
import PageHeader from "@/components/common/PageHeader.vue";
import SearchToolbar from "@/components/common/SearchToolbar.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import { useDebounce } from "@/composables/useDebounce";
import { usePersistentFilters } from "@/composables/usePersistentFilters";
import { useServerTable } from "@/composables/useServerTable";
import {
  getClientes,
  createCliente,
  updateCliente,
  deleteCliente,
} from "@/modules/clientes/api/ClientesServices";

const clientes = ref([]);
const totalItems = ref(0);
const loading = ref(false);
const dialog = ref(false);
const confirmDialog = ref(false);
const editing = ref(false);
const error = ref("");
const selectedCliente = ref(null);
const form = ref(getEmptyForm());

const { filters } = usePersistentFilters("clientes_filters", {
  search: "",
});
const { options, serverParams, updateOptions } = useServerTable({
  ordering: "nombre",
});

const headers = [
  { title: "Nombre", key: "nombre" },
  { title: "Identificación", key: "identificacion" },
  { title: "Teléfono", key: "telefono", sortable: false },
  { title: "Correo", key: "correo", sortable: false },
  { title: "Estado", key: "estado", sortable: false },
  { title: "Acciones", key: "actions", sortable: false },
];

const debouncedLoad = useDebounce(() => {
  options.page = 1;
  cargarClientes();
});

function getEmptyForm() {
  return {
    id: null,
    nombre: "",
    identificacion: "",
    telefono: "",
    correo: "",
    direccion: "",
    estado: true,
  };
}

async function cargarClientes() {
  loading.value = true;
  error.value = "";

  try {
    const data = await getClientes({
      ...serverParams.value,
      search: filters.search || undefined,
    });

    clientes.value = data.results || data;
    totalItems.value = data.count ?? clientes.value.length;
  } catch (err) {
    error.value = err.response?.data?.detail || "No se pudieron cargar los clientes.";
  } finally {
    loading.value = false;
  }
}

function onTableOptions(value) {
  updateOptions(value);
  cargarClientes();
}

function abrirCrear() {
  editing.value = false;
  form.value = getEmptyForm();
  dialog.value = true;
}

function abrirEditar(cliente) {
  editing.value = true;
  form.value = { ...cliente };
  dialog.value = true;
}

function pedirEliminar(cliente) {
  selectedCliente.value = cliente;
  confirmDialog.value = true;
}

async function guardarCliente() {
  try {
    if (editing.value) {
      await updateCliente(form.value.id, form.value);
    } else {
      await createCliente(form.value);
    }

    dialog.value = false;
    await cargarClientes();
  } catch (err) {
    error.value = JSON.stringify(err.response?.data || "No se pudo guardar el cliente.");
  }
}

async function confirmarEliminar() {
  if (!selectedCliente.value) return;

  try {
    await deleteCliente(selectedCliente.value.id);
    confirmDialog.value = false;
    selectedCliente.value = null;
    await cargarClientes();
  } catch (err) {
    error.value = "No se pudo eliminar el cliente.";
  }
}

watch(() => filters.search, debouncedLoad);

onMounted(cargarClientes);
</script>

<template>
  <section>
    <PageHeader
      title="Clientes"
      subtitle="Gestión de clientes registrados en el sistema."
      button-text="Nuevo cliente"
      @click="abrirCrear"
    />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
      {{ error }}
    </v-alert>

    <v-card>
      <SearchToolbar
        v-model="filters.search"
        label="Buscar cliente"
        @search="cargarClientes"
      />

      <v-skeleton-loader
        v-if="loading && !clientes.length"
        type="table"
        class="mx-4 mb-4"
      />

      <v-data-table-server
        v-else
        :headers="headers"
        :items="clientes"
        :items-length="totalItems"
        :loading="loading"
        :items-per-page="options.itemsPerPage"
        item-value="id"
        @update:options="onTableOptions"
      >
        <template #item.estado="{ item }">
          <v-chip
            :color="item.estado ? 'green' : 'grey'"
            size="small"
            variant="tonal"
          >
            {{ item.estado ? "Activo" : "Inactivo" }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-btn icon="mdi-pencil" variant="text" size="small" @click="abrirEditar(item)" />
          <v-btn icon="mdi-delete" variant="text" size="small" color="error" @click="pedirEliminar(item)" />
        </template>
      </v-data-table-server>
    </v-card>

    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title>
          {{ editing ? "Editar cliente" : "Nuevo cliente" }}
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-text-field v-model="form.nombre" label="Nombre" variant="outlined" density="compact" required />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field v-model="form.identificacion" label="Identificación" variant="outlined" density="compact" />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field v-model="form.telefono" label="Teléfono" variant="outlined" density="compact" />
            </v-col>

            <v-col cols="12">
              <v-text-field v-model="form.correo" label="Correo" type="email" variant="outlined" density="compact" />
            </v-col>

            <v-col cols="12">
              <v-textarea v-model="form.direccion" label="Dirección" variant="outlined" density="compact" rows="2" />
            </v-col>

            <v-col cols="12">
              <v-switch v-model="form.estado" label="Cliente activo" color="primary" />
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="guardarCliente">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar cliente"
      :message="`¿Desea eliminar el cliente ${selectedCliente?.nombre || ''}?`"
      @confirm="confirmarEliminar"
    />
  </section>
</template>
