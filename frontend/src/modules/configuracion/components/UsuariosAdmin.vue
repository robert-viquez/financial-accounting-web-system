<script setup>
import { onMounted, reactive, ref } from 'vue'
import {
  createUsuario,
  deleteUsuario,
  getRoles,
  getUsuarios,
  setUsuarioPassword,
  updateUsuario,
} from '@/modules/configuracion/api/configuracionService'

defineProps({ currentUserId: Number, isSuperuser: Boolean })
const emit = defineEmits(['message'])
const usuarios = ref([])
const roles = ref([])
const search = ref('')
const dialog = ref(false)
const passwordDialog = ref(false)
const editing = ref(null)
const form = reactive({
  username: '',
  first_name: '',
  last_name: '',
  correo: '',
  roles: [],
  is_active: true,
  is_staff: false,
  password: '',
})
const password = ref('')

const notify = (text, color = 'success') => emit('message', text, color)
const errorText = (error, fallback) =>
  error.response?.data?.detail || Object.values(error.response?.data || {})?.[0]?.[0] || fallback

async function load() {
  const [userData, roleData] = await Promise.all([
    getUsuarios({ search: search.value, page_size: 100 }),
    getRoles(),
  ])
  usuarios.value = userData.results ?? userData
  roles.value = roleData
}

function openUser(user = null) {
  editing.value = user
  Object.assign(
    form,
    user
      ? { ...user, roles: [...user.roles], password: '' }
      : {
          username: '',
          first_name: '',
          last_name: '',
          correo: '',
          roles: [],
          is_active: true,
          is_staff: false,
          password: '',
        },
  )
  dialog.value = true
}

async function saveUser() {
  try {
    if (editing.value) await updateUsuario(editing.value.id, form)
    else await createUsuario(form)
    dialog.value = false
    await load()
    notify(editing.value ? 'Usuario actualizado.' : 'Usuario creado.')
  } catch (error) {
    notify(errorText(error, 'No se pudo guardar el usuario.'), 'error')
  }
}

async function toggleActive(user) {
  try {
    await updateUsuario(user.id, { is_active: !user.is_active })
    await load()
    notify(user.is_active ? 'Usuario desactivado.' : 'Usuario reactivado.')
  } catch (error) {
    notify(errorText(error, 'No se pudo cambiar el estado.'), 'error')
  }
}

function openPassword(user) {
  editing.value = user
  password.value = ''
  passwordDialog.value = true
}
async function savePassword() {
  try {
    await setUsuarioPassword(editing.value.id, password.value)
    passwordDialog.value = false
    notify('Contraseña actualizada.')
  } catch (error) {
    notify(errorText(error, 'No se pudo actualizar la contraseña.'), 'error')
  }
}

async function removeUser(user) {
  if (!window.confirm(`¿Eliminar permanentemente a ${user.username}? Prefiera desactivarlo.`))
    return
  try {
    await deleteUsuario(user.id)
    await load()
    notify('Usuario eliminado.')
  } catch (error) {
    notify(errorText(error, 'No se puede eliminar; desactive el usuario.'), 'error')
  }
}

onMounted(load)
</script>

<template>
  <v-card>
    <v-card-title class="d-flex align-center ga-3">
      Usuarios
      <v-spacer />
      <v-text-field
        v-model="search"
        label="Buscar"
        prepend-inner-icon="mdi-magnify"
        density="compact"
        hide-details
        clearable
        max-width="320"
        @keyup.enter="load"
      />
      <v-btn color="primary" prepend-icon="mdi-account-plus" @click="openUser()"
        >Crear usuario</v-btn
      >
    </v-card-title>
    <v-table density="compact">
      <thead>
        <tr>
          <th>Usuario</th>
          <th>Nombre</th>
          <th>Roles</th>
          <th>Estado</th>
          <th>Privilegio</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in usuarios" :key="user.id">
          <td>{{ user.username }}</td>
          <td>{{ user.nombre }}</td>
          <td>
            <v-chip v-for="role in user.roles" :key="role" class="mr-1" size="small">{{
              role
            }}</v-chip>
          </td>
          <td>
            <v-chip :color="user.is_active ? 'success' : 'default'" size="small">{{
              user.is_active ? 'Activo' : 'Inactivo'
            }}</v-chip>
          </td>
          <td>
            {{
              user.is_superuser
                ? 'Superusuario'
                : user.is_staff
                  ? 'Administrador de negocio'
                  : 'Usuario'
            }}
          </td>
          <td class="text-no-wrap">
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              :disabled="user.is_superuser && !isSuperuser"
              @click="openUser(user)"
            />
            <v-btn
              icon="mdi-key"
              size="small"
              variant="text"
              :disabled="user.is_superuser && !isSuperuser"
              @click="openPassword(user)"
            />
            <v-btn
              :icon="user.is_active ? 'mdi-account-off' : 'mdi-account-check'"
              size="small"
              variant="text"
              :disabled="user.id === currentUserId || user.is_superuser"
              @click="toggleActive(user)"
            />
            <v-btn
              v-if="isSuperuser"
              icon="mdi-delete"
              color="error"
              size="small"
              variant="text"
              :disabled="user.id === currentUserId || user.is_superuser"
              @click="removeUser(user)"
            />
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-card>

  <v-dialog v-model="dialog" max-width="620"
    ><v-card
      ><v-card-title>{{ editing ? 'Editar usuario' : 'Crear usuario' }}</v-card-title
      ><v-card-text
        ><v-row>
          <v-col cols="12" sm="6"
            ><v-text-field v-model="form.username" label="Usuario" :disabled="!!editing"
          /></v-col>
          <v-col cols="12" sm="6"
            ><v-text-field
              v-if="!editing"
              v-model="form.password"
              label="Contraseña inicial"
              type="password"
          /></v-col>
          <v-col cols="12" sm="6"><v-text-field v-model="form.first_name" label="Nombre" /></v-col>
          <v-col cols="12" sm="6"
            ><v-text-field v-model="form.last_name" label="Apellidos"
          /></v-col>
          <v-col cols="12"
            ><v-text-field v-model="form.correo" label="Correo" type="email"
          /></v-col>
          <v-col cols="12"
            ><v-select
              v-model="form.roles"
              :items="roles"
              item-title="name"
              item-value="name"
              label="Roles"
              multiple
              chips
          /></v-col>
          <v-col cols="6"
            ><v-switch v-model="form.is_active" label="Activo" color="primary"
          /></v-col>
          <v-col v-if="isSuperuser" cols="6"
            ><v-switch v-model="form.is_staff" label="Administrador de negocio" color="primary"
          /></v-col> </v-row></v-card-text
      ><v-card-actions
        ><v-spacer /><v-btn @click="dialog = false">Cancelar</v-btn
        ><v-btn color="primary" @click="saveUser">Guardar</v-btn></v-card-actions
      ></v-card
    ></v-dialog
  >

  <v-dialog v-model="passwordDialog" max-width="480"
    ><v-card
      ><v-card-title>Establecer contraseña</v-card-title
      ><v-card-text
        ><p class="mb-4">Usuario: {{ editing?.username }}</p>
        <v-text-field v-model="password" label="Nueva contraseña" type="password" /></v-card-text
      ><v-card-actions
        ><v-spacer /><v-btn @click="passwordDialog = false">Cancelar</v-btn
        ><v-btn color="primary" @click="savePassword">Actualizar</v-btn></v-card-actions
      ></v-card
    ></v-dialog
  >
</template>
