// src/shims-vue.d.ts
declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
}

// 声明 lang 模块
declare module '@/lang/index' {
    import type { I18n } from 'vue-i18n'
    const i18n: I18n
    export default i18n
}

// 声明 lang/index.ts 模块
declare module './lang/index' {
    import type { I18n } from 'vue-i18n'
    const i18n: I18n
    export default i18n
}

// 声明其他 JS 模块
declare module '*.js' {
    const content: any
    export default content
}