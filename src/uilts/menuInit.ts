// src/utils/menuInit.ts
import { getMenuConfig, listVersions } from '@/api/system_api'
import type { useCounterStore } from '@/stores/counter'

/**
 * 初始化菜单和版本数据
 * @param counterStore - Pinia store 实例
 * @returns Promise
 */
export async function initMenuData(counterStore: ReturnType<typeof useCounterStore>) {
    try {
        counterStore.setLoading(true)

        // 1. 获取所有版本列表
        const versionsRes = await listVersions()
        if (versionsRes.code !== 200 || !versionsRes.data) {
            throw new Error('Failed to load versions')
        }

        const versions = versionsRes.data
        counterStore.setAllVersions(versions)

        // 2. 获取默认版本（优先 is_default，否则取第一个）
        const defaultVersion = versions.find((v: any) => v.is_default) || versions[0]
        if (!defaultVersion) {
            throw new Error('No version available')
        }

        const currentVersionCode = defaultVersion.version_code
        counterStore.setMenuVersion(currentVersionCode)

        // 3. 获取当前版本的菜单配置
        const menuRes = await getMenuConfig(currentVersionCode)
        if (menuRes.code !== 200 || !menuRes.data) {
            throw new Error('Failed to load menu config')
        }

        counterStore.setMenuConfig(menuRes.data)

        return {
            success: true,
            version: currentVersionCode,
            menuCount: menuRes.data.length
        }
    } catch (error) {
        console.error('Failed to initialize menu:', error)
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error'
        }
    } finally {
        counterStore.setLoading(false)
    }
}

/**
 * 切换版本并重新加载菜单
 * @param counterStore - Pinia store 实例
 * @param versionCode - 目标版本代码
 * @returns Promise
 */
export async function switchVersion(counterStore: ReturnType<typeof useCounterStore>, versionCode: string) {
    try {
        counterStore.setLoading(true)

        // 检查版本是否存在
        const versionExists = counterStore.allVersions.some((v: any) => v.version_code === versionCode)
        if (!versionExists) {
            throw new Error(`Version ${versionCode} not found`)
        }

        // 获取新版本的菜单配置
        const menuRes = await getMenuConfig(versionCode)
        if (menuRes.code !== 200 || !menuRes.data) {
            throw new Error('Failed to load menu config')
        }

        // 更新 store
        counterStore.setMenuVersion(versionCode)
        counterStore.setMenuConfig(menuRes.data)

        return {
            success: true,
            version: versionCode,
            menuCount: menuRes.data.length
        }
    } catch (error) {
        console.error('Failed to switch version:', error)
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error'
        }
    } finally {
        counterStore.setLoading(false)
    }
}

/**
 * 刷新当前版本的菜单配置
 * @param counterStore - Pinia store 实例
 * @returns Promise
 */
export async function refreshCurrentMenu(counterStore: ReturnType<typeof useCounterStore>) {
    try {
        counterStore.setLoading(true)

        const currentVersion = counterStore.menuVersion
        const menuRes = await getMenuConfig(currentVersion)
        if (menuRes.code !== 200 || !menuRes.data) {
            throw new Error('Failed to load menu config')
        }

        counterStore.setMenuConfig(menuRes.data)

        return {
            success: true,
            menuCount: menuRes.data.length
        }
    } catch (error) {
        console.error('Failed to refresh menu:', error)
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error'
        }
    } finally {
        counterStore.setLoading(false)
    }
}