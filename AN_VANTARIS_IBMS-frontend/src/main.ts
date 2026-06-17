import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { bootstrapApp } from './app/bootstrap'
import './app/styles.css'

const app = createApp(App)

app.use(router)
app.use(ElementPlus)
bootstrapApp(app, router)
app.mount('#app')
