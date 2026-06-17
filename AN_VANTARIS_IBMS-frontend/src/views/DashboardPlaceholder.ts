import { defineComponent, h } from 'vue'

export default defineComponent({
  name: 'DashboardPlaceholder',
  setup() {
    return () =>
      h('div', { class: 'placeholder-page' }, [
        h('h1', 'Dashboard'),
        h('p', 'Authenticated placeholder — module routes pending.'),
      ])
  },
})
