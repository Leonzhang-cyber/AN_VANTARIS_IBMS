<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { resolveL3RouteContentConfig } from '@/services/menu/l3-content-registry'

const route = useRoute()
const content = computed(() => resolveL3RouteContentConfig(route.query.menu, route.query.l3))
</script>

<template>
  <section v-if="content" class="route-l3-panel" aria-label="Selected menu section content">
    <div class="route-l3-panel__head">
      <div>
        <span class="route-l3-panel__kicker">Selected section</span>
        <h2>{{ content.title }}</h2>
        <p>{{ content.subtitle }}</p>
      </div>
      <el-button type="primary" plain>{{ content.primaryAction }}</el-button>
    </div>

    <div class="route-l3-panel__metrics">
      <article v-for="metric in content.metrics" :key="metric.label" class="route-l3-panel__metric">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <em>{{ metric.note }}</em>
      </article>
    </div>

    <el-table :data="content.rows" stripe border class="route-l3-panel__table">
      <el-table-column prop="item" label="Action" min-width="240" />
      <el-table-column prop="focus" label="Focus Area" min-width="280" />
      <el-table-column prop="status" label="Status" min-width="140" />
    </el-table>
  </section>
</template>

<style scoped>
.route-l3-panel {
  margin-bottom: 18px;
  padding: 18px;
  border: 1px solid #d8e6e1;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
}

.route-l3-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.route-l3-panel__kicker {
  display: block;
  margin-bottom: 6px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel h2 {
  margin: 0;
  color: #10201d;
  font-size: 22px;
}

.route-l3-panel p {
  margin: 8px 0 0;
  max-width: 860px;
  color: #52615d;
  line-height: 1.55;
}

.route-l3-panel__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.route-l3-panel__metric {
  min-width: 0;
  padding: 14px;
  border: 1px solid #e2ece8;
  border-radius: 10px;
  background: #f8fbfa;
}

.route-l3-panel__metric span,
.route-l3-panel__metric em {
  display: block;
  color: #64748b;
  font-size: 12px;
  font-style: normal;
}

.route-l3-panel__metric strong {
  display: block;
  margin: 6px 0;
  color: #0f766e;
  font-size: 18px;
}

@media (max-width: 1100px) {
  .route-l3-panel__head {
    flex-direction: column;
  }

  .route-l3-panel__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .route-l3-panel__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
