import { defineComponent, h } from 'vue'

export default defineComponent({
  name: 'ForbiddenPlaceholder',
  setup() {
    return () =>
      h('div', { class: 'placeholder-page' }, [
        h('h1', '403 Forbidden'),
        h('p', 'You do not have permission to access this resource.'),
      ])
  },
})
