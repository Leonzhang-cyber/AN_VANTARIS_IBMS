<template>
  <div class="page">
    <h3 class="page-title">System Settings</h3>

    <!-- 基础设置 -->
    <el-card class="mb-20">
      <div class="card-title">Basic Configuration</div>
      <el-form label-width="160px" style="margin-top: 15px">
        <el-form-item label="System Name">
          <el-input v-model="form.systemName" style="width: 400px" />
        </el-form-item>
        <el-form-item label="System Logo">
          <el-upload action="/" :show-file-list="false">
            <el-button type="default">Upload Logo</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="Language">
          <el-select v-model="form.language" style="width: 200px">
            <el-option label="English" value="en" />
            <el-option label="Chinese" value="zh" />
          </el-select>
        </el-form-item>
        <el-form-item label="Timezone">
          <el-select v-model="form.timezone" style="width: 200px">
            <el-option label="UTC+8" value="8" />
            <el-option label="UTC+0" value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="Auto Refresh">
          <el-switch v-model="form.autoRefresh" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 安全设置 -->
    <el-card class="mb-20">
      <div class="card-title">Security Settings</div>
      <el-form label-width="160px" style="margin-top: 15px">
        <el-form-item label="Login Password">
          <el-input v-model="form.password" type="password" style="width: 400px" show-password />
        </el-form-item>
        <el-form-item label="Confirm Password">
          <el-input v-model="form.confirmPwd" type="password" style="width: 400px" show-password />
        </el-form-item>
        <el-form-item label="Session Timeout">
          <el-input-number v-model="form.sessionTimeout" :min="15" :max="120" style="width: 200px" />
          <span class="ml-10">Minutes</span>
        </el-form-item>
        <el-form-item label="IP Whitelist Only">
          <el-switch v-model="form.ipWhitelist" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 告警设置 -->
    <el-card class="mb-20">
      <div class="card-title">Alarm Notification Settings</div>
      <el-form label-width="160px" style="margin-top: 15px">
        <el-form-item label="Enable Alarm Push">
          <el-switch v-model="form.alarmEnable" />
        </el-form-item>
        <el-form-item label="Sound Alarm">
          <el-switch v-model="form.alarmSound" />
        </el-form-item>
        <el-form-item label="Email Notification">
          <el-switch v-model="form.emailNotify" />
        </el-form-item>
        <el-form-item label="SMS Notification">
          <el-switch v-model="form.smsNotify" />
        </el-form-item>
        <el-form-item label="Alarm Level">
          <el-checkbox-group v-model="form.alarmLevel">
            <el-checkbox label="Critical" />
            <el-checkbox label="Warning" />
            <el-checkbox label="Info" />
          </el-checkbox-group>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据存储 -->
    <el-card class="mb-20">
      <div class="card-title">Data Storage</div>
      <el-form label-width="160px" style="margin-top: 15px">
        <el-form-item label="History Data Retention">
          <el-select v-model="form.dataRetention" style="width: 200px">
            <el-option label="30 Days" value="30" />
            <el-option label="90 Days" value="90" />
            <el-option label="180 Days" value="180" />
            <el-option label="365 Days" value="365" />
          </el-select>
        </el-form-item>
        <el-form-item label="Auto Clean Logs">
          <el-switch v-model="form.autoCleanLog" />
        </el-form-item>
        <el-form-item label="Auto Backup Database">
          <el-switch v-model="form.autoBackup" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 保存按钮 -->
    <div style="text-align: center; margin-top: 10px">
      <el-button type="primary" size="default" @click="save">
        Save All Settings
      </el-button>
      <el-button style="margin-left: 10px" @click="reset">
        Reset
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const form = reactive({
  systemName: 'IBMS IoT Platform',
  language: 'en',
  timezone: '8',
  autoRefresh: true,

  password: '',
  confirmPwd: '',
  sessionTimeout: 30,
  ipWhitelist: false,

  alarmEnable: true,
  alarmSound: true,
  emailNotify: true,
  smsNotify: false,
  alarmLevel: ['Critical', 'Warning'],

  dataRetention: '90',
  autoCleanLog: true,
  autoBackup: true
})

const save = () => {
  ElMessage.success('All settings saved successfully!')
}

const reset = () => {
  ElMessage.info('All settings have been reset to default')
}
</script>

<style scoped>
.page {
  padding: 12px;
}
.page-title {
  font-size: 19px;
  font-weight: 600;
  margin-bottom: 20px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
}
.mb-20 {
  margin-bottom: 20px;
}
.ml-10 {
  margin-left: 10px;
}
</style>