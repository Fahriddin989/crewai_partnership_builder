<template>
  <div>
    <RouterLink to="/organizations">← Back to Organizations</RouterLink>
    <p v-if="organizationLoading">Loading organization…</p><p v-else-if="organizationError" class="error">{{ organizationError }}</p>
    <template v-else>
      <div class="page-heading"><div><h1>{{ organization.name }}</h1><p>{{ organizationType }}</p></div></div>
      <div class="detail-card"><p><strong>Country:</strong> {{ organization.country || '—' }}</p><p><strong>Website:</strong> <a v-if="organization.website" :href="organization.website" target="_blank" rel="noopener">{{ organization.website }}</a><span v-else>—</span></p><p v-if="organization.description"><strong>Description:</strong> {{ organization.description }}</p></div>
      <section class="section-heading"><h2>Agreements</h2><button class="primary small-button" @click="showAgreementForm = !showAgreementForm">+ Add Agreement</button></section>
      <form v-if="showAgreementForm" class="detail-card simple-form" @submit.prevent="createAgreement">
        <p v-if="agreementFormError" class="error">{{ agreementFormError }}</p>
        <p v-for="(errors, field) in agreementFieldErrors" :key="field" class="error">{{ field }}: {{ errors.join(', ') }}</p>
        <label>Title<input v-model="agreementForm.title" required></label>
        <label>Agreement type<select v-model="agreementForm.agreement_type" required><option value="" disabled>Select type</option><option v-for="(label, value) in agreementTypeLabels" :key="value" :value="value">{{ label }}</option></select></label>
        <label>Status<select v-model="agreementForm.status" required><option v-for="(label, value) in agreementStatusLabels" :key="value" :value="value">{{ label }}</option></select></label>
        <label>Description<textarea v-model="agreementForm.description"></textarea></label>
        <label>Signed date<input v-model="agreementForm.signed_date" type="date"></label><label>Start date<input v-model="agreementForm.start_date" type="date"></label><label>Expiration date<input v-model="agreementForm.expiration_date" type="date"></label>
        <div><button class="primary" :disabled="agreementSubmitting">Create Agreement</button> <button type="button" @click="resetAgreementForm">Cancel</button></div>
      </form>
      <p v-if="agreementsLoading">Loading agreements…</p><p v-else-if="agreementsError" class="error">{{ agreementsError }}</p><p v-else-if="agreements.length === 0" class="empty">No agreements have been recorded for this organization.</p>
      <div v-else class="table-wrap"><table><thead><tr><th>Title</th><th>Type</th><th>Status</th><th>Signed date</th><th>Start date</th><th>Expiration date</th></tr></thead><tbody><tr v-for="agreement in agreements" :key="agreement.id"><td><RouterLink :to="`/agreements/${agreement.id}`">{{ agreement.title }}</RouterLink></td><td>{{ agreementTypeLabels[agreement.agreement_type] || agreement.agreement_type }}</td><td><span class="status-badge">{{ agreementStatusLabels[agreement.status] || agreement.status }}</span></td><td>{{ agreement.signed_date || '—' }}</td><td>{{ agreement.start_date || '—' }}</td><td>{{ agreement.expiration_date || '—' }}</td></tr></tbody></table></div>
      <section class="section-heading"><h2>Photo reports</h2><button class="primary small-button" @click="showMediaForm = !showMediaForm">+ Add Photo Report</button></section>
      <form v-if="showMediaForm" class="detail-card simple-form" @submit.prevent="createMedia"><p v-if="mediaFormError" class="error">{{ mediaFormError }}</p><label>Title<input v-model="mediaForm.title" required></label><label>Image<input type="file" accept="image/*" required @change="mediaForm.image = $event.target.files[0]"></label><label>Description<textarea v-model="mediaForm.description"></textarea></label><label class="checkbox"><input v-model="mediaForm.is_public" type="checkbox"> Public</label><div><button class="primary" :disabled="mediaSubmitting">Upload Photo Report</button> <button type="button" @click="resetMediaForm">Cancel</button></div></form>
      <p v-if="mediaLoading">Loading photo reports…</p><p v-else-if="mediaError" class="error">{{ mediaError }}</p><p v-else-if="media.length === 0" class="empty">No photo reports recorded.</p><div v-else class="media-grid"><article v-for="item in media" :key="item.id" class="detail-card media-card"><img :src="item.image" :alt="item.title"><strong>{{ item.title }}</strong><p v-if="item.description">{{ item.description }}</p><small>{{ formatDate(item.uploaded_at) }} · <span>{{ item.is_public ? 'Public' : 'Private' }}</span></small></article></div>
    </template>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import client from '../api/client'
import { ORGANIZATION_TYPE_LABELS, AGREEMENT_TYPE_LABELS, AGREEMENT_STATUS_LABELS } from '../constants/partnerships'
const route = useRoute(), organization = ref(null), agreements = ref([]), media = ref([]), organizationLoading = ref(true), agreementsLoading = ref(true), mediaLoading = ref(true), organizationError = ref(''), agreementsError = ref(''), mediaError = ref('')
const showAgreementForm = ref(false), showMediaForm = ref(false), agreementSubmitting = ref(false), mediaSubmitting = ref(false), agreementFormError = ref(''), mediaFormError = ref(''), agreementFieldErrors = ref({})
const agreementTypeLabels = AGREEMENT_TYPE_LABELS, agreementStatusLabels = AGREEMENT_STATUS_LABELS, organizationType = computed(() => ORGANIZATION_TYPE_LABELS[organization.value?.organization_type] || organization.value?.organization_type)
const blankAgreement = () => ({ title: '', agreement_type: '', status: 'DRAFT', description: '', signed_date: '', start_date: '', expiration_date: '' }), blankMedia = () => ({ title: '', image: null, description: '', is_public: false })
const agreementForm = ref(blankAgreement()), mediaForm = ref(blankMedia())
const formatDate = value => value ? new Date(value).toLocaleDateString() : '—', list = data => Array.isArray(data) ? data : (data.results || [])
const errorText = error => error.response?.status === 403 ? 'You do not have permission to perform this action.' : 'Unable to save. Please review the form.'
async function loadAgreements() { agreementsLoading.value = true; try { agreements.value = list((await client.get('/api/agreements/', { params: { organization: route.params.id } })).data); agreementsError.value = '' } catch { agreementsError.value = 'Unable to load agreements.' } finally { agreementsLoading.value = false } }
async function loadMedia() { mediaLoading.value = true; try { media.value = list((await client.get('/api/organization-media/', { params: { organization: route.params.id } })).data); mediaError.value = '' } catch { mediaError.value = 'Unable to load photo reports.' } finally { mediaLoading.value = false } }
function resetAgreementForm() { agreementForm.value = blankAgreement(); agreementFormError.value = ''; agreementFieldErrors.value = {}; showAgreementForm.value = false }
function resetMediaForm() { mediaForm.value = blankMedia(); mediaFormError.value = ''; showMediaForm.value = false }
async function createAgreement() { agreementSubmitting.value = true; agreementFormError.value = ''; agreementFieldErrors.value = {}; try { await client.post('/api/agreements/', { ...agreementForm.value, organization: Number(route.params.id), signed_date: agreementForm.value.signed_date || null, start_date: agreementForm.value.start_date || null, expiration_date: agreementForm.value.expiration_date || null }); resetAgreementForm(); await loadAgreements() } catch (error) { agreementFormError.value = error.response?.data && typeof error.response.data === 'object' && error.response.status !== 403 ? '' : errorText(error); agreementFieldErrors.value = error.response?.status !== 403 && error.response?.data && typeof error.response.data === 'object' ? error.response.data : {} } finally { agreementSubmitting.value = false } }
async function createMedia() { mediaSubmitting.value = true; mediaFormError.value = ''; const data = new FormData(); data.append('organization', route.params.id); data.append('title', mediaForm.value.title); data.append('image', mediaForm.value.image); data.append('description', mediaForm.value.description); data.append('is_public', mediaForm.value.is_public); try { await client.post('/api/organization-media/', data); resetMediaForm(); await loadMedia() } catch (error) { mediaFormError.value = errorText(error) } finally { mediaSubmitting.value = false } }
onMounted(async () => { try { organization.value = (await client.get(`/api/organizations/${route.params.id}/`)).data } catch (error) { organizationError.value = error.response?.status === 404 ? 'Organization not found.' : 'Unable to load organization.' } finally { organizationLoading.value = false }; await Promise.all([loadAgreements(), loadMedia()]) })
</script>
