<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  createRol,
  deleteRol,
  getPermisos,
  getRoles,
  updateRol,
} from '@/modules/configuracion/api/configuracionService'

const emit = defineEmits(['message'])
const roles = ref([])
const permisos = ref([])
const dialog = ref(false)
const editing = ref(null)
const form = reactive({ name: '', permisos: [] })
const grouped = computed(() =>
  permisos.value.reduce((result, item) => {
    if (!result[item.aplicacion]) result[item.aplicacion] = []
    result[item.aplicacion].push(item)
    return result
  }, {}),
)
const notify = (text, color = 'success') => emit('message', text, color)

async function load() {
  ;[roles.value, permisos.value] = await Promise.all([getRoles(), getPermisos()])
}
function openRole(role = null) {
  editing.value = role
  Object.assign(
    form,
    role ? { name: role.name, permisos: [...role.permisos] } : { name: '', permisos: [] },
  )
  dialog.value = true
}
async function saveRole() {
  try {
    if (editing.value) await updateRol(editing.value.id, form)
    else await createRol(form)
    dialog.value = false
    await load()
    notify(editing.value ? 'Rol actualizado.' : 'Rol creado.')
  } catch (error) {
    notify(error.response?.data?.detail || 'No se pudo guardar el rol.', 'error')
  }
}
async function removeRole(role) {
  if (!window.confirm(`¿Eliminar el rol ${role.name}?`)) return
  try {
    await deleteRol(role.id)
    await load()
    notify('Rol eliminado.')
  } catch (error) {
    notify(error.response?.data?.detail || 'No se puede eliminar un rol en uso.', 'error')
  }
}
onMounted(load)
</script>

<template>
  <v-card>
    <v-card-title class="d-flex align-center"
      >Roles y permisos<v-spacer /><v-btn
        color="primary"
        prepend-icon="mdi-shield-plus"
        @click="openRole()"
        >Crear rol</v-btn
      ></v-card-title
    >
    <v-card-subtitle
      >Los permisos nativos de Django se asignan a grupos; los usuarios reciben acceso mediante sus
      roles.</v-card-subtitle
    >
    <v-list lines="two">
      <v-list-item
        v-for="role in roles"
        :key="role.id"
        :title="role.name"
        :subtitle="`${role.usuarios.length} usuario(s) · ${role.permisos.length} permiso(s)`"
      >
        <template #append
          ><v-btn icon="mdi-pencil" variant="text" @click="openRole(role)" /><v-btn
            icon="mdi-delete"
            color="error"
            variant="text"
            :disabled="role.usuarios.length > 0"
            @click="removeRole(role)"
        /></template>
      </v-list-item>
    </v-list>
  </v-card>

  <v-dialog v-model="dialog" max-width="760"
    ><v-card
      ><v-card-title>{{ editing ? 'Editar rol' : 'Crear rol' }}</v-card-title
      ><v-card-text>
        <v-text-field v-model="form.name" label="Nombre del rol" />
        <v-expansion-panels multiple>
          <v-expansion-panel
            v-for="(items, app) in grouped"
            :key="app"
            :title="app.charAt(0).toUpperCase() + app.slice(1)"
            ><v-expansion-panel-text>
              <v-checkbox
                v-for="permission in items"
                :key="permission.id"
                v-model="form.permisos"
                :value="permission.id"
                :label="permission.name"
                density="compact"
                hide-details
              /> </v-expansion-panel-text
          ></v-expansion-panel>
        </v-expansion-panels> </v-card-text
      ><v-card-actions
        ><v-spacer /><v-btn @click="dialog = false">Cancelar</v-btn
        ><v-btn color="primary" @click="saveRole">Guardar</v-btn></v-card-actions
      ></v-card
    ></v-dialog
  >
</template>
