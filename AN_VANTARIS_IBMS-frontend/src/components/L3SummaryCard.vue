<script setup lang="ts">
defineProps<{
  kicker?: string
  title: string
  description?: string
  primaryAction?: string
  actionAriaLabel?: string
}>()

const emit = defineEmits<{
  (event: 'primary-action'): void
}>()
</script>

<template>
  <section class="l3-summary-card" :class="{ 'l3-summary-card--with-action': primaryAction }">
    <div class="l3-summary-card__header">
      <div class="l3-summary-card__copy">
        <span v-if="kicker" class="l3-summary-card__kicker">{{ kicker }}</span>
        <h2>{{ title }}</h2>
        <p v-if="description">{{ description }}</p>
      </div>

      <el-button
        v-if="primaryAction"
        class="l3-summary-card__cta"
        type="primary"
        plain
        :aria-label="actionAriaLabel ?? primaryAction"
        @click="emit('primary-action')"
      >
        {{ primaryAction }}
      </el-button>
    </div>

    <div v-if="$slots.default" class="l3-summary-card__body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.l3-summary-card {
  box-sizing: border-box;
  display: block;
  padding: 8px 0 14px;
  border: none !important;
  border-radius: 0;
  background: transparent !important;
  box-shadow: none !important;
  overflow: visible;
}

.l3-summary-card--with-action {
  padding-right: 0;
}

.l3-summary-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 32px;
  flex-wrap: wrap;
  min-width: 0;
}

.l3-summary-card__copy {
  min-width: 0;
  flex: 1 1 auto;
  max-width: 860px;
}

.l3-summary-card__kicker {
  display: block;
  margin-bottom: 5px;
  color: #6b7c78;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.l3-summary-card h2 {
  margin: 0;
  color: #10201d;
  font-size: 22px;
  line-height: 1.22;
}

.l3-summary-card p {
  margin: 8px 0 0;
  max-width: 820px;
  color: #52615d;
  font-size: 14px;
  line-height: 1.55;
}

.l3-summary-card__cta {
  flex: 0 0 auto;
  margin-left: auto;
  width: auto;
  min-height: 38px;
  padding: 8px 20px;
  border: 1px solid #0f766e !important;
  border-color: #0f766e !important;
  background: #ffffff !important;
  color: #0f766e !important;
  font-weight: 700;
  box-shadow: none !important;
  white-space: nowrap;
}

.l3-summary-card :deep(.l3-summary-card__cta.el-button),
.l3-summary-card :deep(.l3-summary-card__cta.el-button.el-button--primary),
.l3-summary-card :deep(.l3-summary-card__cta.el-button.el-button--primary.is-plain) {
  --el-button-text-color: #0f766e;
  --el-button-bg-color: #ffffff;
  --el-button-border-color: #0f766e;
  --el-button-hover-text-color: #0f766e;
  --el-button-hover-bg-color: #f0fdfa;
  --el-button-hover-border-color: #0f766e;
  --el-button-active-text-color: #0f766e;
  --el-button-active-bg-color: #ecfdf5;
  --el-button-active-border-color: #0f766e;
  border-color: #0f766e !important;
  background: #ffffff !important;
  color: #0f766e !important;
}

.l3-summary-card :deep(.l3-summary-card__cta.el-button span) {
  color: #0f766e !important;
}

.l3-summary-card__cta:hover,
.l3-summary-card__cta:focus,
.l3-summary-card :deep(.l3-summary-card__cta.el-button:hover),
.l3-summary-card :deep(.l3-summary-card__cta.el-button:focus),
.l3-summary-card :deep(.l3-summary-card__cta.el-button.el-button--primary.is-plain:hover),
.l3-summary-card :deep(.l3-summary-card__cta.el-button.el-button--primary.is-plain:focus) {
  border-color: #0f766e !important;
  background: #f0fdfa !important;
  color: #0f766e !important;
}

.l3-summary-card :deep(.l3-summary-card__cta.el-button:hover span),
.l3-summary-card :deep(.l3-summary-card__cta.el-button:focus span) {
  color: #0f766e !important;
}

.l3-summary-card__body {
  margin-top: 18px;
}

@media (max-width: 1100px) {
  .l3-summary-card,
  .l3-summary-card--with-action {
    padding: 8px 0 14px;
  }

  .l3-summary-card__header {
    gap: 14px;
  }

  .l3-summary-card__cta {
    margin-left: 0;
  }
}
</style>
