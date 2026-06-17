import { defineComponent, h } from 'vue'

export default defineComponent({
  name: 'NotFoundPlaceholder',
  setup() {
    return () =>
      h('div', { class: 'placeholder-page' }, [
        h('h1', '404 Not Found'),
        h('p', 'The requested page does not exist.'),
      ])
  },
})
