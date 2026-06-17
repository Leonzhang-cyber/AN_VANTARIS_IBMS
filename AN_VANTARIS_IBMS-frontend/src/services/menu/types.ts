export type MenuItemSource = 'backend' | 'static'

export interface AppMenuItem {
  id: string
  label: string
  path: string
  icon?: string
  permission?: string
  children?: AppMenuItem[]
  source?: MenuItemSource
}
