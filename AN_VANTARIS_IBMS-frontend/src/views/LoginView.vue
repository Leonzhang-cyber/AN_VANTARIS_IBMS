<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import * as didApi from '@/services/api/did'
import { extractAccessToken, persistLoginSession } from '@/services/auth/session'

const router = useRouter()
const route = useRoute()

const form = reactive({
  did: '',
  challenge: '',
  signature: '',
})

const loading = ref(false)
const errorMessage = ref('')

async function onSubmit(): Promise<void> {
  errorMessage.value = ''
  loading.value = true

  try {
    const payload = {
      did: form.did.trim(),
      challenge: form.challenge.trim(),
      signature: form.signature.trim(),
    }

    if (!payload.did || !payload.challenge || !payload.signature) {
      errorMessage.value = 'DID, challenge, and signature are required.'
      return
    }

    const response = await didApi.login(payload)
    const token = extractAccessToken(response)

    if (!token) {
      errorMessage.value = 'Login succeeded but no access token was returned.'
      return
    }

    persistLoginSession(token, { did: payload.did })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    await router.push(redirect)
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.message || 'Login failed.'
    } else {
      errorMessage.value = 'Login failed.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1>VANTARIS IBMS</h1>
      <p class="login-subtitle">DID challenge login</p>

      <form class="login-form" @submit.prevent="onSubmit">
        <label>
          DID
          <input v-model="form.did" type="text" name="did" autocomplete="username" required />
        </label>

        <label>
          Challenge
          <input v-model="form.challenge" type="text" name="challenge" autocomplete="off" required />
        </label>

        <label>
          Signature
          <input v-model="form.signature" type="text" name="signature" autocomplete="off" required />
        </label>

        <p v-if="errorMessage" class="login-error" role="alert">
          {{ errorMessage }}
        </p>

        <button type="submit" class="login-submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: #eef2f7;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgb(15 23 42 / 8%);
}

.login-card h1 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
}

.login-subtitle {
  margin: 0 0 1.5rem;
  color: #64748b;
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.login-form input {
  padding: 0.55rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.95rem;
}

.login-error {
  margin: 0;
  color: #b91c1c;
  font-size: 0.875rem;
}

.login-submit {
  margin-top: 0.25rem;
  padding: 0.65rem 1rem;
  border: none;
  border-radius: 6px;
  background: #0f172a;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.login-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style>
