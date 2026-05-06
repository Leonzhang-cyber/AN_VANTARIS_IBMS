<template>
  <div class="home">
    <h1>{{ $t('welcome') }}</h1>
    <p>{{ $t('home') }}</p>
    <button @click="switchLang('zh')">中文</button>
    <button @click="switchLang('en')">English</button>
  </div>
</template>
<!--测试-->

<script setup>
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()

const switchLang = (lang) => {
  locale.value = lang
}
</script>

<style scoped>
.home {
  padding: 20px;
  text-align: center;
}
</style>