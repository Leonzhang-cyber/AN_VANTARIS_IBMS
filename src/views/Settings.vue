<template>
  <div class="page">
    <h3 class="page-title">System Settings</h3>

    <el-card>
      <div class="card-title">Basic Configuration</div>
      <el-form label-width="150px" style="margin-top:15px">
        <el-form-item label="System Name">
          <el-input model-value="IBMS IoT Platform" />
        </el-form-item>
        <el-form-item label="Language">
          <el-select v-model="lang" style="width:200px">
            <el-option label="English" value="en" />
            <el-option label="Chinese" value="zh" />
          </el-select>
        </el-form-item>
        <el-form-item label="Auto Refresh">
          <el-switch v-model="refresh" />
        </el-form-item>
        <el-form-item label="Alarm Notification">
          <el-switch v-model="alarm" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary">Save Settings</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const lang = ref('en')
const refresh = ref(true)
const alarm = ref(true)
</script>

<style scoped>
.page{padding:12px}
.page-title{font-size:19px;font-weight:600;margin-bottom:20px}
.card-title{font-size:16px;font-weight:600;margin-bottom:15px}
</style>