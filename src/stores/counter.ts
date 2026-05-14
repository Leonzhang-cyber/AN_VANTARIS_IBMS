// src/stores/counter.ts
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }

  // 添加全屏状态
  const isFullscreen = ref(false)
  function setFullscreen(value: boolean) {
    isFullscreen.value = value
  }

  // 新增：节能模式状态
  const isEnergySavingActive = ref(true)
  function setEnergySavingActive(value: boolean) {
    isEnergySavingActive.value = value
  }
  function toggleEnergySaving() {
    isEnergySavingActive.value = !isEnergySavingActive.value
  }

  // 新增：报告显示状态
  const showEnergyReport = ref(false)
  function setShowEnergyReport(value: boolean) {
    showEnergyReport.value = value
  }
  function toggleShowEnergyReport() {
    showEnergyReport.value = !showEnergyReport.value
  }

  return {
    count,
    doubleCount,
    increment,
    isFullscreen,
    setFullscreen,
    isEnergySavingActive,
    setEnergySavingActive,
    toggleEnergySaving,
    showEnergyReport,
    setShowEnergyReport,
    toggleShowEnergyReport
  }
})