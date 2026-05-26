// src/utils/menuInit.js
import { getMenuConfig, listVersions, getDefaultVersion } from '@/api/system_api'
import { ElMessage } from 'element-plus'

/**
 * 初始化菜单和版本数据
 */
export async function initMenuData(counterStore) {
    try {
        counterStore.setLoading(true)

        console.log('=== 开始初始化菜单数据 ===')

        // 1. 获取默认版本
        const defaultVersionRes = await getDefaultVersion()
        console.log('默认版本响应:', defaultVersionRes)

        if (!defaultVersionRes) {
            throw new Error('Failed to get default version')
        }

        // 获取默认版本的 version_code
        const currentVersionCode = defaultVersionRes.version_code
        console.log('当前版本代码:', currentVersionCode)

        // 设置当前版本
        counterStore.setMenuVersion(currentVersionCode)

        // 2. 获取所有版本列表（用于版本切换下拉菜单）
        const allVersionsRes = await listVersions()
        if (allVersionsRes) {
            counterStore.setAllVersions(allVersionsRes)
            console.log('所有版本列表:', allVersionsRes.map(v => v.version_code))
        }

        // 3. 使用默认版本的 version_code 获取菜单配置
        console.log('开始获取菜单配置，版本:', currentVersionCode)
        const menuRes = await getMenuConfig(currentVersionCode)
        console.log('菜单配置响应:', menuRes)

        if (!menuRes) {
            throw new Error(menuRes.message || 'Failed to load menu config')
        }

        // 设置菜单配置到 store
        counterStore.setMenuConfig(menuRes)
        console.log('菜单配置设置成功，共', menuRes.length, '个顶级菜单')
        console.log('菜单数据:', JSON.stringify(menuRes, null, 2))

        return {
            success: true,
            version: currentVersionCode,
            menuCount: menuRes.length
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
 */
export async function switchVersion(counterStore, versionCode) {
    try {
        counterStore.setLoading(true)

        console.log('切换版本:', versionCode)

        // 获取新版本的菜单配置
        const menuRes = await getMenuConfig(versionCode)
        console.log('新版本菜单配置:', menuRes)

        if (!menuRes) {
            throw new Error('Failed to load menu config')
        }

        // 更新 store
        counterStore.setMenuVersion(versionCode)
        counterStore.setMenuConfig(menuRes)

        console.log('版本切换成功，菜单数量:', menuRes.length)

        return {
            success: true,
            version: versionCode,
            menuCount: menuRes.length
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

        const menuRes = await getMenuConfig(currentVersion)
        if (!menuRes) {
            throw new Error('Failed to load menu config')
        }

        counterStore.setMenuConfig(menuRes)
        console.log('菜单刷新成功，数量:', menuRes.length)

        return {
            success: true,
            menuCount: menuRes.length
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