<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import * as authApi from '@/services/api/auth'
import { extractAccessToken, persistLoginSession } from '@/services/auth/session'

const router = useRouter()
const route = useRoute()

const form = reactive({
  username: '',
  password: '',
  otp: '',
})

const loading = ref(false)
const errorMessage = ref('')

async function onSubmit(): Promise<void> {
  errorMessage.value = ''
  loading.value = true

  try {
    const payload = {
      username: form.username.trim(),
      password: form.password,
      otp: form.otp.trim(),
    }

    if (!payload.username || !payload.password || !payload.otp) {
      errorMessage.value = 'Username, password, and 2FA code are required.'
      return
    }

    const response = await authApi.login(payload)
    const token = extractAccessToken(response)

    if (!token) {
      errorMessage.value = 'Login succeeded but no access token was returned.'
      return
    }

    persistLoginSession(token, {
      username: response.user?.username ?? payload.username,
      displayName: response.user?.displayName ?? payload.username,
      role: response.user?.role ?? 'Admin',
      permissions: response.user?.permissions ?? [],
      authMode: 'password_2fa',
    })

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
      <div class="brand-block">
        <p class="brand-eyebrow">VANTARIS ONE</p>
        <h1>Secure Operations Login</h1>
        <p class="login-subtitle">Username, password, and 2FA verification</p>
      </div>

      <form class="login-form" @submit.prevent="onSubmit">
        <label>
          Username
          <input
            v-model="form.username"
            type="text"
            name="username"
            autocomplete="username"
            required
          />
        </label>

        <label>
          Password
          <input
            v-model="form.password"
            type="password"
            name="password"
            autocomplete="current-password"
            required
          />
        </label>

        <label>
          2FA Code
          <input
            v-model="form.otp"
            type="text"
            name="otp"
            inputmode="numeric"
            autocomplete="one-time-code"
            maxlength="6"
            required
          />
        </label>

        <p v-if="errorMessage" class="login-error" role="alert">
          {{ errorMessage }}
        </p>

        <button type="submit" class="login-submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <div class="login-note">
        <strong>Review account</strong>
        <span>admin / Admin@2026 / 260624</span>
      </div>
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
  background:
    radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 28rem),
    linear-gradient(135deg, #f5fbf8 0%, #eef5ff 54%, #f8fafc 100%);
}

.login-card {
  width: 100%;
  max-width: 460px;
  padding: 2rem;
  background: #fff;
  border: 1px solid #dbe7e4;
  border-radius: 18px;
  box-shadow: 0 20px 48px rgb(15 23 42 / 12%);
}

.brand-block {
  margin-bottom: 1.5rem;
}

.brand-eyebrow {
  margin: 0 0 0.45rem;
  color: #0f766e;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.login-card h1 {
  margin: 0 0 0.45rem;
  color: #0f172a;
  font-size: 1.65rem;
}

.login-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
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
  color: #334155;
  font-size: 0.875rem;
  font-weight: 700;
}

.login-form input {
  padding: 0.7rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  color: #0f172a;
  font-size: 0.98rem;
  outline: none;
}

.login-form input:focus {
  border-color: #0f766e;
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.12);
}

.login-error {
  margin: 0;
  color: #b91c1c;
  font-size: 0.875rem;
}

.login-submit {
  margin-top: 0.25rem;
  padding: 0.78rem 1rem;
  border: none;
  border-radius: 10px;
  background: #0f766e;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}

.login-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.login-note {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.2rem;
  padding: 0.8rem;
  border: 1px solid #dbe7e4;
  border-radius: 12px;
  background: #f8fbfa;
  color: #475569;
  font-size: 0.82rem;
}

.login-note strong {
  color: #0f766e;
}
</style>
