<template>
  <div class="login-container">
    <!-- 左侧品牌区 -->
    <div class="brand-section">
      <div class="brand-content">
        <div class="logo-wrapper">
          <div class="logo-icon">
            <span class="icon">🏢</span>
          </div>
        </div>
        <span class="system-name">AegisNexus IBMS</span>
        <span class="system-slogan">Intelligent Building Management System</span>

        <div class="divider"></div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-card-inner">
              <span class="feature-icon">🔗</span>
              <div class="feature-text">
                <span class="feature-title">DID Authentication</span>
                <span class="feature-desc">Decentralized identity management</span>
              </div>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-card-inner">
              <span class="feature-icon">🌐</span>
              <div class="feature-text">
                <span class="feature-title">IoT Integration</span>
                <span class="feature-desc">Real-time device monitoring</span>
              </div>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-card-inner">
              <span class="feature-icon">📊</span>
              <div class="feature-text">
                <span class="feature-title">Data Modeling</span>
                <span class="feature-desc">Entity relationship management</span>
              </div>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-card-inner">
              <span class="feature-icon">⛓️</span>
              <div class="feature-text">
                <span class="feature-title">Blockchain</span>
                <span class="feature-desc">Immutable audit trail</span>
              </div>
            </div>
          </div>
        </div>

        <span class="version">v2.0.0</span>
      </div>
    </div>

    <!-- 右侧登录区 -->
    <div class="login-section">
      <div class="login-card">
        <div class="welcome">
          <span class="welcome-title">Welcome Back</span>
          <span class="welcome-subtitle">Secure login with DID and Private Key</span>
        </div>

        <!-- 登录方式切换 -->
        <div class="login-tabs">
          <div
              class="tab-item"
              :class="{ active: loginMode === 'vc' }"
              @click="switchMode('vc')"
          >
            <span>📜 File Login</span>
          </div>
          <div
              class="tab-item"
              :class="{ active: loginMode === 'manual' }"
              @click="switchMode('manual')"
          >
            <span>🔑 Manual Login</span>
          </div>
        </div>

        <div class="form">
          <!-- 文件登录模式 -->
          <div v-if="loginMode === 'vc'">
            <div class="input-group">
              <span class="input-label">Credential File</span>
              <div class="file-upload-area" @click="selectVCFile">
                <span class="upload-icon">📦</span>
                <span class="upload-text" v-if="!vcFileInfo">
                  Click to upload credential file (VC + Private Key)
                </span>
                <div v-else class="file-info">
                  <span class="file-name">{{ vcFileInfo.name }}</span>
                  <span class="file-size">{{ vcFileInfo.size }} bytes</span>
                  <span class="file-status">✅ Loaded</span>
                </div>
              </div>
            </div>

            <div v-if="vcData" class="vc-info">
              <div class="info-title">📋 Credential Information</div>
              <div class="info-row">
                <span class="info-label">Name:</span>
                <span class="info-value">{{ userName }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">DID:</span>
                <span class="info-value">{{ userDid }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Public Key:</span>
                <span class="info-value">{{ userPublicKey }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Expiration:</span>
                <span class="info-value">{{ expirationDate }}</span>
              </div>
              <div class="info-row" v-if="hasPrivateKey">
                <span class="info-label">Private Key:</span>
                <span class="info-value private-key-status">✅ Auto extracted</span>
              </div>
            </div>

            <div class="input-group">
              <span class="input-label">Challenge Code</span>
              <div class="input-wrapper challenge-wrapper">
                <span class="input-icon">🎲</span>
                <input
                    class="input-field"
                    v-model="challenge"
                    placeholder="Click 'Get'"
                    disabled
                />
                <button
                    class="get-challenge-btn"
                    @click="getChallenge"
                    :disabled="challengeLoading || !vcData"
                >
                  {{ challengeLoading ? 'Get' : 'Get' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 手动登录模式 -->
          <div v-else>
            <div class="input-group">
              <span class="input-label">DID Identifier</span>
              <div class="input-wrapper">
                <span class="input-icon">🔑</span>
                <input
                    class="input-field"
                    v-model="did"
                    placeholder="Enter DID"
                />
              </div>
            </div>

            <div class="input-group">
              <span class="input-label">Private Key</span>
              <div class="input-wrapper">
                <span class="input-icon">🔒</span>
                <input
                    class="input-field"
                    :type="showPrivateKey ? 'text' : 'password'"
                    v-model="privateKey"
                    placeholder="Enter private key (64 hex chars)"
                />
                <span class="eye-icon" @click="showPrivateKey = !showPrivateKey">
                  {{ showPrivateKey ? '🙈' : '👁️' }}
                </span>
              </div>
            </div>

            <div class="input-group">
              <span class="input-label">Challenge Code</span>
              <div class="input-wrapper challenge-wrapper">
                <span class="input-icon">🎲</span>
                <input
                    class="input-field"
                    v-model="challenge"
                    placeholder="Click 'Get'"
                    disabled
                />
                <button
                    class="get-challenge-btn"
                    @click="getChallengeForManual"
                    :disabled="challengeLoading || !did"
                >
                  {{ challengeLoading ? 'Getting...' : 'Get' }}
                </button>
              </div>
            </div>
          </div>

          <div class="security-tip">
            <span class="tip-icon">🔐</span>
            <span class="tip-text">Private key is used locally for signing and will not be uploaded to the server</span>
          </div>

          <button class="login-btn" @click="handleLogin" :disabled="loading">
            <span v-if="!loading">Login</span>
            <span v-else>Logging in...</span>
          </button>
        </div>

        <div class="copyright">
          <span>© 2024 AegisNexus All rights reserved.</span>
        </div>
      </div>
    </div>

    <!-- 进度弹窗 -->
    <div class="progress-overlay" v-if="showProgressOverlay">
      <div class="progress-container">
        <div class="progress-spinner">
          <span class="progress-icon">{{ progressIcon }}</span>
        </div>
        <span class="progress-step">{{ progressStep }}</span>
        <span class="progress-title">{{ progressTitle }}</span>
        <span class="progress-message">{{ progressMessage }}</span>
        <div class="progress-bar-wrapper">
          <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ethers } from 'ethers'
import { generateChallenge, generateVP, login } from '@/api/did_api.js'

// 登录模式
const loginMode = ref('vc')

// 表单数据
const did = ref('')
const challenge = ref('')
const privateKey = ref('')
const showPrivateKey = ref(false)

// VC 模式相关数据
const vcFileInfo = ref(null)
const vcData = ref(null)
const userDid = ref('')
const userName = ref('')
const userPublicKey = ref('')
const expirationDate = ref('')
const hasPrivateKey = ref(false)

// 状态
const loading = ref(false)
const challengeLoading = ref(false)

// 进度弹窗
const showProgressOverlay = ref(false)
const progressIcon = ref('⏳')
const progressStep = ref('')
const progressTitle = ref('')
const progressMessage = ref('')
const progressPercent = ref(0)

// 生成签名
const generateSignature = async (privateKeyHex, message) => {
  const formattedKey = privateKeyHex.startsWith('0x') ? privateKeyHex : '0x' + privateKeyHex
  const wallet = new ethers.Wallet(formattedKey)
  const signature = await wallet.signMessage(message)
  return signature
}

const showProgress = (step, title, message, percent = 0) => {
  showProgressOverlay.value = true
  progressStep.value = step
  progressTitle.value = title
  progressMessage.value = message
  progressPercent.value = percent
}

const updateProgress = (step, title, message, percent) => {
  progressStep.value = step
  progressTitle.value = title
  progressMessage.value = message
  progressPercent.value = percent
}

const hideProgress = () => {
  showProgressOverlay.value = false
}

const switchMode = (mode) => {
  loginMode.value = mode
  clearFormData()
}

const clearFormData = () => {
  did.value = ''
  challenge.value = ''
  privateKey.value = ''
  vcFileInfo.value = null
  vcData.value = null
  userDid.value = ''
  userName.value = ''
  userPublicKey.value = ''
  expirationDate.value = ''
  hasPrivateKey.value = false
}

const showToast = (message, type = 'info') => {
  if (type === 'error') {
    ElMessage.error(message)
  } else if (type === 'success') {
    ElMessage.success(message)
  } else {
    ElMessage.info(message)
  }
}

// 选择文件
const selectVCFile = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    vcFileInfo.value = {
      name: file.name,
      size: file.size
    }

    const reader = new FileReader()
    reader.onload = (event) => {
      parseVCContent(event.target.result)
    }
    reader.readAsText(file, 'utf-8')
  }
  input.click()
}

// 解析文件内容
const parseVCContent = (content) => {
  try {
    const fileData = JSON.parse(content)

    let vcContent = fileData.vc || fileData

    // 提取私钥
    if (fileData.private_key) {
      let extractedPrivateKey = fileData.private_key
      if (extractedPrivateKey.startsWith('0x')) {
        extractedPrivateKey = extractedPrivateKey.substring(2)
      }
      privateKey.value = extractedPrivateKey
      hasPrivateKey.value = true
    } else if (fileData.privateKey) {
      let extractedPrivateKey = fileData.privateKey
      if (extractedPrivateKey.startsWith('0x')) {
        extractedPrivateKey = extractedPrivateKey.substring(2)
      }
      privateKey.value = extractedPrivateKey
      hasPrivateKey.value = true
    }

    vcData.value = vcContent

    if (vcContent.credentialSubject) {
      userDid.value = vcContent.credentialSubject.id || ''
      userName.value = vcContent.credentialSubject.name || ''
      userPublicKey.value = vcContent.credentialSubject.public_key || ''
      did.value = userDid.value
    }

    if (vcContent.expirationDate) {
      expirationDate.value = vcContent.expirationDate.split('T')[0]
    }

    showToast('File parsed successfully', 'success')
  } catch (error) {
    console.error('解析文件失败:', error)
    showToast('Failed to parse file', 'error')
  }
}

// 获取挑战码（文件模式）
const getChallenge = async () => {
  if (!userDid.value) {
    showToast('Please upload credential file first', 'info')
    return
  }

  challengeLoading.value = true

  try {
    const res = await generateChallenge(32)
    challenge.value = res.challenge
    showToast('Challenge code obtained successfully', 'success')
  } catch (error) {
    showToast('Failed to get challenge code: ' + error.message, 'error')
  } finally {
    challengeLoading.value = false
  }
}

// 获取挑战码（手动模式）
const getChallengeForManual = async () => {
  if (!did.value.trim()) {
    showToast('Please enter DID', 'info')
    return
  }

  challengeLoading.value = true

  try {
    const res = await generateChallenge(32)
    challenge.value = res.challenge
    showToast('Challenge code obtained successfully', 'success')
  } catch (error) {
    showToast('Failed to get challenge code: ' + error.message, 'error')
  } finally {
    challengeLoading.value = false
  }
}

// 生成 VP（文件模式）
const generateVPWrapper = async () => {
  const requestData = {
    holder_did: userDid.value,
    holder_private_key: privateKey.value,
    vcs: [vcData.value],
    challenge: challenge.value
  }
  return await generateVP(requestData)
}

// VP 登录
const loginWithVP = async (vp, vpChallenge) => {
  return await login({ vp, challenge: vpChallenge })
}

// Challenge 模式登录（手动模式）
const loginWithChallenge = async (didValue, signature, challengeValue) => {
  return await login({ did: didValue, challenge: challengeValue, signature })
}

// 登录处理
const handleLogin = async () => {
  if (loginMode.value === 'vc') {
    // 文件模式：生成 VP 后登录
    if (!vcData.value) {
      showToast('Please upload credential file first', 'info')
      return
    }

    if (!privateKey.value.trim() || privateKey.value.length !== 64) {
      showToast('Private key is invalid', 'error')
      return
    }

    if (!challenge.value.trim()) {
      showToast('Please get challenge code first', 'info')
      return
    }

    loading.value = true

    try {
      showProgress('1/3', 'Generate VP', 'Building Verifiable Presentation...', 0)
      progressIcon.value = '🔐'

      const vp = await generateVPWrapper()
      updateProgress('2/3', 'Verify Identity', 'Verifying identity information...', 50)
      progressIcon.value = '🔑'

      const res = await loginWithVP(vp, challenge.value)
      const token = res.token

      updateProgress('3/3', 'Login Success', 'Redirecting...', 90)
      progressIcon.value = '✅'

      localStorage.setItem('token', token)
      localStorage.setItem('userInfo', JSON.stringify({
        did: userDid.value,
        name: userName.value,
        public_key: userPublicKey.value
      }))

      setTimeout(() => {
        hideProgress()
        showToast('Login successful, redirecting...', 'success')
        setTimeout(() => {
          window.location.href = '/'
        }, 500)
      }, 500)
    } catch (error) {
      hideProgress()
      showToast('Login failed: ' + error.message, 'error')
    } finally {
      loading.value = false
    }

  } else {
    // 手动模式：直接签名登录（Challenge 模式）
    if (!did.value.trim()) {
      showToast('Please enter DID', 'info')
      return
    }

    if (!privateKey.value.trim()) {
      showToast('Please enter private key', 'info')
      return
    }

    if (!/^[0-9a-fA-F]{64}$/.test(privateKey.value.trim())) {
      showToast('Invalid private key format, must be 64 hex characters', 'error')
      return
    }

    if (!challenge.value.trim()) {
      showToast('Please get challenge code first', 'info')
      return
    }

    loading.value = true

    try {
      showProgress('1/2', 'Generate Signature', 'Signing the challenge...', 0)
      progressIcon.value = '🔐'

      const signature = await generateSignature(privateKey.value, challenge.value)
      updateProgress('2/2', 'Verify Identity', 'Verifying identity information...', 50)
      progressIcon.value = '🔑'

      const res = await loginWithChallenge(did.value, signature, challenge.value)
      const token = res.token

      updateProgress('2/2', 'Login Success', 'Redirecting...', 90)
      progressIcon.value = '✅'

      localStorage.setItem('token', token)
      localStorage.setItem('userInfo', JSON.stringify({
        did: did.value,
        name: '',
        public_key: ''
      }))

      setTimeout(() => {
        hideProgress()
        showToast('Login successful, redirecting...', 'success')
        setTimeout(() => {
          window.location.href = '/'
        }, 500)
      }, 500)
    } catch (error) {
      hideProgress()
      showToast('Login failed: ' + error.message, 'error')
    } finally {
      loading.value = false
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式保持不变 */
.login-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  background: #f5f7fa;
}

.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    width: 150%;
    height: 150%;
    background: radial-gradient(circle at 30% 50%, rgba(0, 212, 255, 0.08) 0%, transparent 50%);
    animation: pulse 8s ease-in-out infinite;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

.brand-content {
  position: relative;
  z-index: 1;
  padding: 40px;
  max-width: 550px;
  width: 100%;
}

.logo-wrapper {
  margin-bottom: 28px;
}

.logo-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #00d4ff, #7b2ff7);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 40px -10px rgba(0, 212, 255, 0.3);

  .icon {
    font-size: 40px;
  }
}

.system-name {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.system-slogan {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 1px;
}

.divider {
  width: 50px;
  height: 2px;
  background: linear-gradient(90deg, #00d4ff, transparent);
  margin: 28px 0 24px 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
  min-height: 100px;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(0, 212, 255, 0.3);
    transform: translateY(-2px);
  }
}

.feature-card-inner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 14px;
}

.feature-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.feature-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
  word-break: break-word;
}

.feature-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.4;
  word-break: break-word;
}

.version {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  text-align: center;
  margin-top: 16px;
}

.login-section {
  width: 460px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.05);
}

.login-card {
  width: 100%;
  max-width: 360px;
  padding: 48px 32px;
}

.login-tabs {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  border-bottom: 1px solid #e5e7eb;

  .tab-item {
    flex: 1;
    text-align: center;
    padding: 12px 0;
    font-size: 14px;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;

    &.active {
      color: #00d4ff;

      &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(135deg, #00d4ff, #7b2ff7);
      }
    }
  }
}

.welcome {
  margin-bottom: 36px;
}

.welcome-title {
  display: block;
  font-size: 26px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.welcome-subtitle {
  display: block;
  font-size: 13px;
  color: #6b7280;
}

.form {
  margin-bottom: 28px;
}

.input-group {
  margin-bottom: 20px;
}

.input-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border-radius: 12px;
  padding: 0 14px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s;

  &:focus-within {
    border-color: #00d4ff;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
  }
}

.challenge-wrapper {
  padding-right: 8px;
}

.input-icon {
  font-size: 16px;
  margin-right: 10px;
  color: #9ca3af;
}

.input-field {
  flex: 1;
  height: 44px;
  font-size: 14px;
  color: #1f2937;
  background: transparent;
  border: none;
  outline: none;
}

.get-challenge-btn {
  background: linear-gradient(135deg, #00d4ff, #7b2ff7);
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 12px;
  color: #fff;
  margin: auto;
  margin-top: 5px;
  margin-bottom: 5px;
  margin-left: 0px;
  white-space: nowrap;
  cursor: pointer;

  &:active {
    transform: scale(0.96);
  }

  &[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.eye-icon {
  font-size: 16px;
  padding: 0 6px;
  color: #9ca3af;
  cursor: pointer;
}

.file-upload-area {
  background: #f9fafb;
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #00d4ff;
    background: #f0fdf4;
  }

  .upload-icon {
    font-size: 40px;
    display: block;
    margin-bottom: 12px;
  }

  .upload-text {
    font-size: 14px;
    color: #6b7280;
  }

  .file-info {
    .file-name {
      display: block;
      font-size: 14px;
      color: #1f2937;
      margin-bottom: 4px;
      word-break: break-all;
    }

    .file-size {
      font-size: 12px;
      color: #9ca3af;
    }

    .file-status {
      display: inline-block;
      margin-top: 8px;
      font-size: 12px;
      color: #10b981;
    }
  }
}

.vc-info {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;

  .info-title {
    font-size: 14px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e5e7eb;
  }

  .info-row {
    display: flex;
    margin-bottom: 8px;
    font-size: 13px;

    &:last-child {
      margin-bottom: 0;
    }

    .info-label {
      width: 120px;
      color: #6b7280;
      flex-shrink: 0;
    }

    .info-value {
      flex: 1;
      color: #1f2937;
      word-break: break-all;

      &.private-key-status {
        color: #10b981;
        font-weight: 500;
      }
    }
  }
}

.security-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  margin-bottom: 24px;
  padding: 10px;
  background: #f0fdf4;
  border-radius: 8px;

  .tip-icon {
    font-size: 14px;
  }

  .tip-text {
    font-size: 12px;
    color: #166534;
  }
}

.login-btn {
  width: 100%;
  height: 44px;
  background: linear-gradient(135deg, #00d4ff, #7b2ff7);
  border-radius: 12px;
  border: none;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;

  &:active {
    transform: scale(0.98);
  }

  &[disabled] {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.copyright {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
  font-size: 10px;
  color: #9ca3af;
}

.progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.progress-container {
  background: #fff;
  border-radius: 24px;
  padding: 32px 40px;
  width: 300px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);

  .progress-spinner {
    margin-bottom: 20px;
  }

  .progress-icon {
    font-size: 56px;
    display: inline-block;
    animation: progressPulse 1.5s ease-in-out infinite;
  }

  .progress-step {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: #00d4ff;
    margin-bottom: 8px;
  }

  .progress-title {
    display: block;
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }

  .progress-message {
    display: block;
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 24px;
  }

  .progress-bar-wrapper {
    width: 100%;
    height: 6px;
    background: #e5e7eb;
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(135deg, #00d4ff, #7b2ff7);
    border-radius: 3px;
    transition: width 0.3s ease;
  }
}

@keyframes progressPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.95); }
}

@media (max-width: 768px) {
  .brand-section {
    display: none;
  }

  .login-section {
    width: 100%;
  }
}
</style>