<script setup>
import { onMounted, ref } from "vue";

import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import PageHeader from "@/components/common/PageHeader.vue";
import SearchToolbar from "@/components/common/SearchToolbar.vue";
import {
  createCategoria,
  deleteCategoria,
  getCategorias,
  updateCategoria,
} from "@/modules/inventario/api/CategoriasServices";

const categorias = ref([]);
const loading = ref(false);
const dialog = ref(false);
const confirmDialog = ref(false);
const editing = ref(false);
const search = ref("");
const error = ref("");
const selectedCategoria = ref(null);
const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("success");

const form = ref(getEmptyForm());

const headers = [
  { title: "Nombre", key: "nombre" },
  { title: "Descripción", key: "descripcion" },
  { title: "Estado", key: "estado" },
  { title: "Acciones", key: "actions", sortable: false },
];

function getEmptyForm() {
  return {
    id: null,
    nombre: "",
    descripcion: "",
    estado: true,
  };
}

function normalizar(response) {
  return response.results ?? response;
}

function mostrarMensaje(texto, color = "success") {
  snackbarText.value = texto;
  snackbarColor.value = color;
  snackbar.value = true;
}

async function cargarCategorias() {
  loading.value = true;
  error.value = "";

  try {
    const data = await getCategorias({
      search: search.value || undefined,
      ordering: "nombre",
    });

    categorias.value = normalizar(data);
  } catch (err) {
    error.value = "No se pudieron cargar las categorías.";
  } finally {
    loading.value = false;
  }
}

function abrirCrear() {
  editing.value = false;
  form.value = getEmptyForm();
  dialog.value = true;
}

function abrirEditar(categoria) {
  editing.value = true;
  form.value = { ...categoria };
  dialog.value = true;
}

function pedirEliminar(categoria) {
  selectedCategoria.value = categoria;
  confirmDialog.value = true;
}

async function guardarCategoria() {
  if (!form.value.nombre) {
    mostrarMensaje("El nombre es obligatorio.", "error");
    return;
  }

  try {
    if (editing.value) {
      await updateCategoria(form.value.id, form.value);
      mostrarMensaje("Categoría actualizada correctamente.");
    } else {
      await createCategoria(form.value);
      mostrarMensaje("Categoría creada correctamente.");
    }

    dialog.value = false;
    await cargarCategorias();
  } catch (err) {
    mostrarMensaje("No se pudo guardar la categoría.", "error");
  }
}

async function confirmarEliminar() {
  if (!selectedCategoria.value) return;

  try {
    await deleteCategoria(selectedCategoria.value.id);
    confirmDialog.value = false;
    selectedCategoria.value = null;
    mostrarMensaje("Categoría eliminada correctamente.");
    await cargarCategorias();
  } catch (err) {
    mostrarMensaje("No se pudo eliminar la categoría.", "error");
  }
}

onMounted(cargarCategorias);
</script>

<template>
  <section>
    <PageHeader
      title="Categorías"
      subtitle="Administración de categorías para clasificar productos."
      button-text="Nueva categoría"
      @click="abrirCrear"
    />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
      {{ error }}
    </v-alert>

    <v-card>
      <SearchToolbar
        v-model="search"
        label="Buscar categoría"
        @search="cargarCategorias"
      />

      <v-data-table
        :headers="headers"
        :items="categorias"
        :loading="loading"
        item-value="id"
      >
        <template #item.estado="{ item }">
          <v-chip
            :color="item.estado ? 'green' : 'grey'"
            size="small"
            variant="tonal"
          >
            {{ item.estado ? "Activa" : "Inactiva" }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-pencil"
            variant="text"
            size="small"
            @click="abrirEditar(item)"
          />
          <v-btn
            icon="mdi-delete"
            variant="text"
            size="small"
            color="error"
            @click="pedirEliminar(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="620">
      <v-card>
        <v-card-title>
          {{ editing ? "Editar categoría" : "Nueva categoría" }}
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="form.nombre"
                label="Nombre"
                variant="outlined"
                density="compact"
                required
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="form.descripcion"
                label="Descripción"
                variant="outlined"
                density="compact"
                rows="2"
              />
            </v-col>

            <v-col cols="12">
              <v-switch
                v-model="form.estado"
                label="Categoría activa"
                color="primary"
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="guardarCategoria">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <ConfirmDialog
      v-model="confirmDialog"
      title="Eliminar categoría"
      :message="`¿Desea eliminar la categoría ${selectedCategoria?.nombre || ''}?`"
      @confirm="confirmarEliminar"
    />

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </section>
</template>
