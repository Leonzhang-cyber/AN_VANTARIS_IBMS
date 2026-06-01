import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia' // 导入 createPinia
import router from './router/index'
import i18n from './lang/index'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 引入 Leaflet CSS
import 'leaflet/dist/leaflet.css'

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')