//src/stores/counter.ts


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

  return { count, doubleCount, increment, isFullscreen, setFullscreen }
})
