/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_IBMS_API_BASE_URL?: string
  readonly VITE_IBMS_APP_NAME?: string
  readonly VITE_IBMS_ENABLE_DEBUG?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
