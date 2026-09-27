<template>
  <div>
    <RouterLink to="/organizations">← Back to Organizations</RouterLink>
    <p v-if="organizationLoading">Loading organization…</p><p v-else-if="organizationError" class="error">{{ organizationError }}</p>
    <template v-else>
      <div class="page-heading"><div><h1>{{ organization.name }}</h1><p>{{ organizationType }}</p></div></div>
      <div class="detail-card"><p><strong>Country:</strong> {{ organization.country || '—' }}</p><p><strong>Website:</strong> <a v-if="organization.website" :href="organization.website" target="_blank" rel="noopener">{{ organization.website }}</a><span v-else>—</span></p><p v-if="organization.description"><strong>Description:</strong> {{ organization.description }}</p></div>
      <h2>Agreements</h2>
      <p v-if="agreementsLoading">Loading agreements…</p><p v-else-if="agreementsError" class="error">{{ agreementsError }}</p><p v-else-if="agreements.length === 0" class="empty">No agreements have been recorded for this organization.</p>
      <div v-else class="table-wrap"><table><thead><tr><th>Title</th><th>Type</th><th>Status</th><th>Signed date</th><th>Start date</th><th>Expiration date</th></tr></thead><tbody><tr v-for="agreement in agreements" :key="agreement.id"><td><RouterLink :to="`/agreements/${agreement.id}`">{{ agreement.title }}</RouterLink></td><td>{{ agreementTypeLabels[agreement.agreement_type] || agreement.agreement_type }}</td><td><span class="status-badge">{{ agreementStatusLabels[agreement.status] || agreement.status }}</span></td><td>{{ agreement.signed_date || '—' }}</td><td>{{ agreement.start_date || '—' }}</td><td>{{ agreement.expiration_date || '—' }}</td></tr></tbody></table></div>
      <h2>Photo reports</h2><p v-if="mediaLoading">Loading photo reports…</p><p v-else-if="mediaError" class="error">{{ mediaError }}</p><p v-else-if="media.length === 0" class="empty">No photo reports recorded.</p><div v-else class="media-grid"><article v-for="item in media" :key="item.id" class="detail-card media-card"><img :src="item.image" :alt="item.title"><strong>{{ item.title }}</strong><p v-if="item.description">{{ item.description }}</p><small>{{ formatDate(item.uploaded_at) }} · <span>{{ item.is_public ? 'Public' : 'Private' }}</span></small></article></div>
    </template>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import client from '../api/client'
import { ORGANIZATION_TYPE_LABELS, AGREEMENT_TYPE_LABELS, AGREEMENT_STATUS_LABELS } from '../constants/partnerships'
const route = useRoute(), organization = ref(null), agreements = ref([]), media = ref([]), organizationLoading = ref(true), agreementsLoading = ref(true), mediaLoading = ref(true), organizationError = ref(''), agreementsError = ref(''), mediaError = ref('')
const organizationType = computed(() => ORGANIZATION_TYPE_LABELS[organization.value?.organization_type] || organization.value?.organization_type), agreementTypeLabels = AGREEMENT_TYPE_LABELS, agreementStatusLabels = AGREEMENT_STATUS_LABELS
const formatDate = value => value ? new Date(value).toLocaleDateString() : '—'
const list = data => Array.isArray(data) ? data : (data.results || [])
onMounted(async () => {
  try { organization.value = (await client.get(`/api/organizations/${route.params.id}/`)).data } catch (error) { organizationError.value = error.response?.status === 404 ? 'Organization not found.' : 'Unable to load organization.' } finally { organizationLoading.value = false }
  try { agreements.value = list((await client.get('/api/agreements/', { params: { organization: route.params.id } })).data) } catch { agreementsError.value = 'Unable to load agreements.' } finally { agreementsLoading.value = false }
  try { media.value = list((await client.get('/api/organization-media/', { params: { organization: route.params.id } })).data) } catch { mediaError.value = 'Unable to load photo reports.' } finally { mediaLoading.value = false }
})
</script>
