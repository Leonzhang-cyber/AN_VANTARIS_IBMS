<script setup lang="ts">
import { View } from "@element-plus/icons-vue";
</script>

<template>
  <div class="not-developed-page">
    <el-empty description="Not Developed Yet">
      <template #image>
        <View size="80" color="#c0c4cc" />
      </template>
      <template #description>
        <span style="font-size: 16px; color: #909399;">Not Developed Yet</span>
      </template>
    </el-empty>
  </div>
</template>

<style scoped>
.not-developed-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>