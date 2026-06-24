export type MenuItemSource = 'backend' | 'static'

export interface AppMenuItem {
  id: string
  label: string
  path: string
  icon?: string
  permission?: string
  children?: AppMenuItem[]
  l3Items?: AppMenuL3Item[]
  source?: MenuItemSource
}

export interface AppMenuL3Item {
  id: string
  label: string
  status?: 'implemented' | 'mapped' | 'gap' | 'planned' | 'innovation'
  mappedExistingModule?: string
  disabled?: boolean
}
