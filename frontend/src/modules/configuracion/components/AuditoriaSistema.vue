<script setup>
import { currentIntlLocale } from "@/i18n/format";
import { onMounted, reactive, ref } from 'vue'
import {
  getAuditoria,
  getInformacionSistema,
} from '@/modules/configuracion/api/configuracionService'

const auditoria = ref([])
const sistema = ref(null)
const filters = reactive({
  search: '',
  metodo: null,
  codigo_respuesta: null,
  desde: null,
  hasta: null,
})
async function loadAudit() {
  const data = await getAuditoria(filters)
  auditoria.value = data.results ?? data
}
onMounted(async () => {
  await Promise.all([
    loadAudit(),
    getInformacionSistema().then((data) => {
      sistema.value = data
    }),
  ])
})
</script>

<template>
  <v-card class="mb-4"
    ><v-card-title>Auditoría</v-card-title
    ><v-card-text
      ><v-row>
        <v-col cols="12" md="4"
          ><v-text-field
            v-model="filters.search"
            label="Usuario o ruta"
            prepend-inner-icon="mdi-magnify"
            clearable
            @keyup.enter="loadAudit"
        /></v-col>
        <v-col cols="6" md="2"
          ><v-select
            v-model="filters.metodo"
            :items="['POST', 'PUT', 'PATCH', 'DELETE']"
            label="Método"
            clearable
        /></v-col>
        <v-col cols="6" md="2"
          ><v-text-field
            v-model="filters.codigo_respuesta"
            label="Código HTTP"
            type="number"
            clearable
        /></v-col>
        <v-col cols="6" md="2"
          ><v-text-field v-model="filters.desde" label="Desde" type="datetime-local" clearable
        /></v-col>
        <v-col cols="6" md="2"
          ><v-text-field
            v-model="filters.hasta"
            label="Hasta"
            type="datetime-local"
            clearable
            @change="loadAudit"
        /></v-col> </v-row
    ></v-card-text>
    <v-table density="compact"
      ><thead>
        <tr>
          <th>Fecha</th>
          <th>Usuario</th>
          <th>Método</th>
          <th>Ruta</th>
          <th>Resultado</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in auditoria" :key="item.id">
          <td>{{ new Date(item.fecha).toLocaleString(currentIntlLocale()) }}</td>
          <td>{{ item.usuario_nombre }}</td>
          <td>{{ item.metodo }}</td>
          <td>{{ item.ruta }}</td>
          <td>
            <v-chip :color="item.codigo_respuesta < 400 ? 'success' : 'error'" size="small">{{
              item.codigo_respuesta
            }}</v-chip>
          </td>
        </tr>
      </tbody></v-table
    >
  </v-card>
  <v-card v-if="sistema"
    ><v-card-title>Información del sistema</v-card-title
    ><v-list density="compact">
      <v-list-item title="Versión" :subtitle="sistema.version_aplicacion" /><v-list-item
        title="Entorno"
        :subtitle="sistema.entorno"
      /><v-list-item title="Backend" :subtitle="sistema.framework" /><v-list-item
        title="Base de datos"
        :subtitle="sistema.base_datos"
      /><v-list-item title="Estado" :subtitle="sistema.estado" /><v-list-item
        title="DEBUG"
        :subtitle="sistema.debug ? 'Activado' : 'Desactivado'"
      /><v-list-item title="HTTPS detectado" :subtitle="sistema.https ? 'Sí' : 'No'" /> </v-list
  ></v-card>
</template>
