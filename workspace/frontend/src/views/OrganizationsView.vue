<template>
  <div>
    <div class="page-heading page-heading-actions">
      <div>
        <h1>Organizations</h1>
        <p>Manage university partnership organizations.</p>
      </div>

      <button class="primary" @click="openCreate">
        + Add Organization
      </button>
    </div>

    <div class="filters">
      <input
        v-model="search"
        placeholder="Search by name..."
      />

      <select v-model="type">
        <option value="">All types</option>

        <option
          v-for="(label, key) in typeLabels"
          :key="key"
          :value="key"
        >
          {{ label }}
        </option>
      </select>
    </div>

    <p v-if="loading">
      Loading organizations...
    </p>

    <p v-else-if="error" class="error">
      {{ error }}
    </p>

    <p v-else-if="filtered.length === 0" class="empty">
      No organizations found.
    </p>

    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Country</th>
            <th>Website</th>
            <th class="actions-column">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="org in filtered"
            :key="org.id"
          >
            <td>
              <RouterLink :to="`/organizations/${org.id}`">
                {{ org.name }}
              </RouterLink>
            </td>

            <td>
              {{ typeLabels[org.organization_type] || org.organization_type }}
            </td>

            <td>
              {{ org.country || '—' }}
            </td>

            <td>
              <a
                v-if="org.website"
                :href="org.website"
                target="_blank"
                rel="noopener"
              >
                {{ org.website }}
              </a>

              <span v-else>—</span>
            </td>

            <td class="actions-cell">
              <details class="action-menu">
                <summary class="action-menu-button">
                  ⋯
                </summary>

                <div class="action-menu-popover">
                  <button
                    type="button"
                    @click="openEdit(org)"
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    class="danger-text"
                    @click="openDelete(org)"
                  >
                    Delete
                  </button>
                </div>
              </details>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <div
      v-if="showForm"
      class="modal-backdrop"
      @click.self="closeForm"
    >
      <div class="modal-card">
        <div class="modal-header">
          <div>
            <h2>
              {{ editingOrganization ? 'Edit Organization' : 'Add Organization' }}
            </h2>

            <p>
              {{
                editingOrganization
                  ? 'Update organization information.'
                  : 'Create a new partner organization.'
              }}
            </p>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="closeForm"
          >
            ×
          </button>
        </div>

        <form
          class="organization-form"
          @submit.prevent="saveOrganization"
        >
          <label>
            Name
            <input
              v-model="form.name"
              required
            />
          </label>

          <label>
            Type
            <select
              v-model="form.organization_type"
              required
            >
              <option
                value=""
                disabled
              >
                Select type
              </option>

              <option
                v-for="(label, key) in typeLabels"
                :key="key"
                :value="key"
              >
                {{ label }}
              </option>
            </select>
          </label>

          <label>
            Country
            <input
              v-model="form.country"
              required
            />
          </label>

          <label>
            Website
            <input
              v-model="form.website"
              type="url"
              placeholder="https://..."
            />
          </label>

          <label class="full-width">
            Description
            <textarea
              v-model="form.description"
              rows="4"
            />
          </label>

          <label class="checkbox full-width">
            <input
              v-model="form.is_public"
              type="checkbox"
            />

            Public organization
          </label>

          <div
            v-if="formError"
            class="error full-width"
          >
            {{ formError }}
          </div>

          <div class="modal-actions full-width">
            <button
              type="button"
              @click="closeForm"
            >
              Cancel
            </button>

            <button
              class="primary"
              :disabled="submitting"
            >
              {{
                submitting
                  ? 'Saving...'
                  : editingOrganization
                    ? 'Save changes'
                    : 'Create Organization'
              }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- DELETE CONFIRMATION -->
    <div
      v-if="organizationToDelete"
      class="modal-backdrop"
      @click.self="cancelDelete"
    >
      <div class="modal-card confirm-card">
        <h2>Delete organization?</h2>

        <p>
          <strong>{{ organizationToDelete.name }}</strong>
          and its related agreements will be deleted.
        </p>

        <p class="muted">
          This action cannot be undone.
        </p>

        <p
          v-if="deleteError"
          class="error"
        >
          {{ deleteError }}
        </p>

        <div class="modal-actions">
          <button
            type="button"
            @click="cancelDelete"
          >
            Cancel
          </button>

          <button
            type="button"
            class="danger-button"
            :disabled="deleting"
            @click="deleteOrganization"
          >
            {{ deleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import client from '../api/client'
import {
  ORGANIZATION_TYPE_LABELS,
} from '../constants/partnerships'


const organizations = ref([])
const loading = ref(true)
const error = ref('')

const search = ref('')
const type = ref('')

const typeLabels = ORGANIZATION_TYPE_LABELS


const showForm = ref(false)
const editingOrganization = ref(null)
const submitting = ref(false)
const formError = ref('')

const organizationToDelete = ref(null)
const deleting = ref(false)
const deleteError = ref('')


function blankForm() {
  return {
    name: '',
    organization_type: '',
    country: '',
    website: '',
    description: '',
    is_public: false,
  }
}


const form = ref(blankForm())


const filtered = computed(() => {
  return organizations.value.filter((organization) => {
    const matchesSearch =
      !search.value ||
      organization.name
        .toLowerCase()
        .includes(search.value.toLowerCase())

    const matchesType =
      !type.value ||
      organization.organization_type === type.value

    return matchesSearch && matchesType
  })
})


async function loadOrganizations() {
  loading.value = true
  error.value = ''

  try {
    const { data } = await client.get(
      '/api/organizations/',
    )

    organizations.value =
      Array.isArray(data)
        ? data
        : data.results || []
  } catch {
    error.value = 'Unable to load organizations.'
  } finally {
    loading.value = false
  }
}


function openCreate() {
  editingOrganization.value = null
  form.value = blankForm()
  formError.value = ''
  showForm.value = true
}


function openEdit(organization) {
  editingOrganization.value = organization

  form.value = {
    name: organization.name || '',
    organization_type:
      organization.organization_type || '',
    country: organization.country || '',
    website: organization.website || '',
    description: organization.description || '',
    is_public: Boolean(organization.is_public),
  }

  formError.value = ''
  showForm.value = true
}


function closeForm(force = false) {
  if (submitting.value && !force) return

  showForm.value = false
  editingOrganization.value = null
  form.value = blankForm()
  formError.value = ''
}

function apiErrorMessage(error) {
  if (error.response?.status === 403) {
    return 'You do not have permission to perform this action.'
  }

  const data = error.response?.data

  if (data && typeof data === 'object') {
    const messages = []

    for (const [field, value] of Object.entries(data)) {
      if (Array.isArray(value)) {
        messages.push(
          `${field}: ${value.join(', ')}`,
        )
      } else {
        messages.push(
          `${field}: ${String(value)}`,
        )
      }
    }

    if (messages.length) {
      return messages.join(' ')
    }
  }

  return 'Unable to save organization.'
}


async function saveOrganization() {
  if (submitting.value) return

  submitting.value = true
  formError.value = ''

  try {
    const payload = {
      ...form.value,
      website: form.value.website.trim(),
    }

    if (editingOrganization.value) {
      await client.patch(
        `/api/organizations/${editingOrganization.value.id}/`,
        payload,
      )
    } else {
      await client.post(
        '/api/organizations/',
        payload,
      )
    }

    closeForm(true)
    await loadOrganizations()
  } catch (err) {
    formError.value = apiErrorMessage(err)
  } finally {
    submitting.value = false
  }
}


function openDelete(organization) {
  organizationToDelete.value = organization
  deleteError.value = ''
}


function cancelDelete() {
  if (deleting.value) return

  organizationToDelete.value = null
  deleteError.value = ''
}


async function deleteOrganization() {
  if (
    deleting.value ||
    !organizationToDelete.value
  ) {
    return
  }

  deleting.value = true
  deleteError.value = ''

  try {
    await client.delete(
      `/api/organizations/${organizationToDelete.value.id}/`,
    )

    organizationToDelete.value = null

    await loadOrganizations()
  } catch (err) {
    if (err.response?.status === 403) {
      deleteError.value =
        'You do not have permission to perform this action.'
    } else {
      deleteError.value =
        'Unable to delete organization.'
    }
  } finally {
    deleting.value = false
  }
}


onMounted(loadOrganizations)
</script>