<template>
  <div>
    <div class="page-heading"><h1>Dashboard</h1><p>Partnership Management Overview</p></div>
    <p v-if="loading" class="empty dashboard-message" role="status">Loading dashboard…</p>
    <div v-else-if="error" class="empty dashboard-message" role="alert"><p class="error">{{ error }}</p><button class="primary" @click="loadDashboard">Retry</button></div>
    <template v-else>
      <section class="dashboard-kpis" aria-label="Partnership statistics">
        <article v-for="metric in metrics" :key="metric.key" class="dashboard-kpi"><span>{{ metric.label }}</span><strong>{{ summary[metric.key] ?? 0 }}</strong></article>
      </section>
      <div class="dashboard-sections">
        <section class="dashboard-panel"><h2>My Organizations</h2>
          <ul v-if="organizations.length" class="dashboard-list"><li v-for="org in organizations" :key="org.id"><RouterLink :to="`/organizations/${org.id}`"><strong>{{ org.name }}</strong><span>{{ organizationType(org.organization_type) }} · {{ org.country || '—' }}</span></RouterLink></li></ul>
          <p v-else class="empty">You don’t have any organizations yet.</p>
        </section>
        <section class="dashboard-panel"><h2>Agreements Expiring Soon</h2>
          <ul v-if="agreements.length" class="dashboard-list"><li v-for="agreement in agreements" :key="agreement.id"><RouterLink :to="`/agreements/${agreement.id}`"><strong>{{ agreement.title }}</strong><span>{{ agreement.organization_name }} · Expires {{ formatDate(agreement.expiration_date) }} <span class="dashboard-days">{{ daysRemaining(agreement.expiration_date) }}</span></span></RouterLink></li></ul>
          <p v-else class="empty">No active agreements expire in the next 30 days.</p>
        </section>
        <section class="dashboard-panel dashboard-followups"><h2>My Follow-ups</h2>
          <ul v-if="followups.length" class="dashboard-list"><li v-for="followup in followups" :key="followup.id"><RouterLink :to="`/organizations/${followup.organization_id}`"><strong>{{ followup.next_step }}</strong><span>{{ followup.organization_name }} · <span class="followup-due" :class="dueClass(followup.follow_up_date)">{{ dueLabel(followup.follow_up_date) }}</span></span></RouterLink></li></ul>
          <p v-else class="empty">No follow-ups are due in the next 14 days.</p>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import client from '../api/client'
import { ORGANIZATION_TYPE_LABELS } from '../constants/partnerships'

const loading = ref(true)
const error = ref('')
const summary = ref({})
const organizations = ref([])
const agreements = ref([])
const followups = ref([])
const metrics = [
  { key: 'total_organizations', label: 'Total Organizations' },
  { key: 'my_organizations', label: 'My Organizations' },
  { key: 'active_agreements', label: 'Active Agreements' },
  { key: 'agreements_expiring_30_days', label: 'Expiring in 30 Days' },
]
const organizationType = value => ORGANIZATION_TYPE_LABELS[value] || value || 'Organization'
const formatDate = value => value ? new Date(`${value}T00:00:00`).toLocaleDateString() : '—'
const dayDelta = value => Math.round((new Date(`${value}T00:00:00`).getTime() - new Date(new Date().toDateString()).getTime()) / 86400000)
const daysRemaining = value => {
  const days = dayDelta(value)
  return days === 0 ? 'Today' : days === 1 ? '1 day left' : `${days} days left`
}
const dueClass = value => dayDelta(value) < 0 ? 'is-overdue' : dayDelta(value) === 0 ? 'is-today' : 'is-future'
const dueLabel = value => {
  const days = dayDelta(value)
  return days < 0 ? `Overdue · ${formatDate(value)}` : days === 0 ? `Due today · ${formatDate(value)}` : `Due ${formatDate(value)}`
}

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/api/dashboard/')
    summary.value = data.summary || {}
    organizations.value = data.my_organizations || []
    agreements.value = data.expiring_agreements || []
    followups.value = data.my_followups || []
  } catch {
    error.value = 'Unable to load the dashboard. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>
