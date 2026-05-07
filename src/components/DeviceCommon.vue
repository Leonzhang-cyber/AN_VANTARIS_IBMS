<!-- DeviceCommon.vue -->
<template>
  <div class="device-page">
    <h3>{{ categoryLabel }} Management</h3>
    <!-- 设备表格等公共内容 -->
  </div>
</template>

<script setup>
defineProps(['category', 'categoryLabel'])
// 根据 category 加载数据
</script>