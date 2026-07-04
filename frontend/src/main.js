import { createApp } from 'vue'
import App from './App.vue'

// 引入全局样式(顺序:token → base → components)
import './assets/styles/tokens.css'
import './assets/styles/base.css'
import './assets/styles/components.css'

createApp(App).mount('#app')