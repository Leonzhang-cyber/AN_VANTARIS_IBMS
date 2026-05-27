// src/utils/menuInit.js
import { listVersions, getActiveVersionMenuConfig, switchActiveVersion } from '@/api/system_api'
import { ElMessage } from 'element-plus'

/**
 * 初始化菜单和版本数据
 */
export async function initMenuData(counterStore) {
    try {
        counterStore.setLoading(true)

        console.log('=== 开始初始化菜单数据 ===')

        // 1. 直接获取当前激活版本的菜单配置（包含版本信息和菜单配置）
        const activeMenuRes = await getActiveVersionMenuConfig()
        console.log('激活版本菜单配置响应:', activeMenuRes)

        if (!activeMenuRes) {
            throw new Error('Failed to get active version menu config')
        }

        // 获取当前激活版本代码
        const currentVersionCode = activeMenuRes.version_code
        const menuConfig = activeMenuRes.menu_config

        console.log('当前激活版本代码:', currentVersionCode)
        console.log('菜单配置:', menuConfig)

        // 设置当前版本
        counterStore.setMenuVersion(currentVersionCode)

        // 设置菜单配置到 store
        counterStore.setMenuConfig(menuConfig)
        console.log('菜单配置设置成功，共', menuConfig.length, '个顶级菜单')

        // 2. 获取所有版本列表（用于版本切换下拉菜单）
        const allVersionsRes = await listVersions()
        if (allVersionsRes && allVersionsRes.length > 0) {
            counterStore.setAllVersions(allVersionsRes)
            console.log('所有版本列表:', allVersionsRes.map(v => v.version_code))
        }

        return {
            success: true,
            version: currentVersionCode,
            menuCount: menuConfig.length
        }
    } catch (error) {
        console.error('初始化菜单失败:', error)
        ElMessage.error(`Failed to load menu: ${error.message}`)
        return {
            success: false,
            error: error.message
        }
    } finally {
        counterStore.setLoading(false)
    }
}

/**
 * 切换版本并重新加载菜单
 * 调用后端接口：切换激活版本 + 返回新版本的菜单配置
 */
export async function switchVersion(counterStore, versionCode) {
    try {
        counterStore.setLoading(true)

        console.log('切换版本:', versionCode)

        // 调用后端接口：切换激活版本并获取新版本菜单配置
        const result = await switchActiveVersion(versionCode)
        console.log('切换版本响应:', result)

        if (!result || !result.menu_config) {
            throw new Error('Failed to switch version')
        }

        // 更新 store
        counterStore.setMenuVersion(result.version_code)
        counterStore.setMenuConfig(result.menu_config)

        // 同时更新版本列表中的 is_default 状态
        const allVersions = counterStore.allVersions
        if (allVersions && allVersions.length > 0) {
            const updatedVersions = allVersions.map(v => ({
                ...v,
                is_default: v.version_code === result.version_code
            }))
            counterStore.setAllVersions(updatedVersions)
        }

        console.log('版本切换成功，菜单数量:', result.menu_config.length)

        return {
            success: true,
            version: result.version_code,
            menuCount: result.menu_config.length,
            menuConfig: result.menu_config
        }
    } catch (error) {
        console.error('切换版本失败:', error)
        ElMessage.error(`Failed to switch version: ${error.message}`)
        return {
            success: false,
            error: error.message
        }
    } finally {
        counterStore.setLoading(false)
    }
}

/**
 * 刷新当前版本的菜单配置
 */
export async function refreshCurrentMenu(counterStore) {
    try {
        counterStore.setLoading(true)

        const currentVersion = counterStore.menuVersion
        console.log('刷新当前版本菜单:', currentVersion)

        // 使用获取激活版本菜单的接口
        const result = await getActiveVersionMenuConfig()
        if (!result || !result.menu_config) {
            throw new Error('Failed to load menu config')
        }

        counterStore.setMenuConfig(result.menu_config)
        console.log('菜单刷新成功，数量:', result.menu_config.length)

        return {
            success: true,
            menuCount: result.menu_config.length
        }
    } catch (error) {
        console.error('Failed to refresh menu:', error)
        ElMessage.error(`Failed to refresh menu: ${error.message}`)
        return {
            success: false,
            error: error.message
        }
    } finally {
        counterStore.setLoading(false)
    }
}