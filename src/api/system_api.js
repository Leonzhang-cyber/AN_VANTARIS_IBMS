// api/system_api.js
/**
 * 系统设置模块 API 封装
 * 对应后端 Flask 路由 /api/system/*
 * 使用 @/utils/request 中封装的 get/post/put/del 方法
 * 请求自动携带 token（如果存在）
 */

import { get, post, put, del } from '@/utils/request.js'

// ==================== 实体类型管理 ====================

/**
 * 创建实体类型
 * @param {Object} data - 实体类型数据
 * @param {string} data.type_code - 类型编码（唯一）
 * @param {string} data.type_name - 类型名称
 * @param {number} data.hierarchy_level - 层级（0系统/1机构/2区域/3设备）
 * @param {string|null} data.parent_type_id - 父类型ID（可选）
 * @returns {Promise}
 */
export function createEntityType(data) {
    return post('/system/entity-types', data)
}

/**
 * 更新实体类型
 * @param {string} typeId - 实体类型ID
 * @param {Object} data - 要更新的字段
 * @returns {Promise}
 */
export function updateEntityType(typeId, data) {
    return put(`/system/entity-types/${typeId}`, data)
}

/**
 * 删除实体类型
 * @param {string} typeId - 实体类型ID
 * @returns {Promise}
 */
export function deleteEntityType(typeId) {
    return del(`/system/entity-types/${typeId}`)
}

/**
 * 查询单个实体类型
 * @param {string} typeId - 实体类型ID
 * @returns {Promise}
 */
export function getEntityType(typeId) {
    return get(`/system/entity-types/${typeId}`)
}

/**
 * 分页查询实体类型列表
 * @param {Object} params - 分页参数
 * @param {number} params.limit - 每页数量（默认100）
 * @param {number} params.offset - 偏移量（默认0）
 * @returns {Promise}
 */
export function listEntityTypes({ limit = 100, offset = 0 } = {}) {
    return get('/system/entity-types', { limit, offset })
}

/**
 * 获取实体类型树（全量层级结构）
 * @returns {Promise}
 */
export function getEntityTypeTree() {
    return get('/system/entity-types/tree')
}

// ==================== 权限管理 ====================

/**
 * 创建权限
 * @param {Object} data - 权限数据
 * @param {string} data.perm_code - 权限编码（唯一）
 * @param {string} data.description - 权限描述
 * @param {Object} [data.extra] - 扩展字段（可选）
 * @returns {Promise}
 */
export function createPermission(data) {
    return post('/system/permissions', data)
}

/**
 * 更新权限
 * @param {string} permId - 权限ID
 * @param {Object} data - 要更新的字段
 * @returns {Promise}
 */
export function updatePermission(permId, data) {
    return put(`/system/permissions/${permId}`, data)
}

/**
 * 删除权限
 * @param {string} permId - 权限ID
 * @returns {Promise}
 */
export function deletePermission(permId) {
    return del(`/system/permissions/${permId}`)
}

/**
 * 查询单个权限
 * @param {string} permId - 权限ID
 * @returns {Promise}
 */
export function getPermission(permId) {
    return get(`/system/permissions/${permId}`)
}

/**
 * 分页查询权限列表
 * @param {Object} params - 分页参数
 * @param {number} params.limit - 每页数量（默认100）
 * @param {number} params.offset - 偏移量（默认0）
 * @returns {Promise}
 */
export function listPermissions({ limit = 100, offset = 0 } = {}) {
    return get('/system/permissions', { limit, offset })
}

// ==================== 标准字段管理 ====================

/**
 * 创建标准字段
 * @param {Object} data - 标准字段数据
 * @returns {Promise}
 */
export function createStandardField(data) {
    return post('/system/standard-fields', data)
}

/**
 * 更新标准字段
 * @param {string} id - 标准字段ID
 * @param {Object} data - 要更新的字段
 * @returns {Promise}
 */
export function updateStandardField(id, data) {
    return put(`/system/standard-fields/${id}`, data)
}

/**
 * 删除标准字段
 * @param {string} id - 标准字段ID
 * @returns {Promise}
 */
export function deleteStandardField(id) {
    return del(`/system/standard-fields/${id}`)
}

/**
 * 查询单个标准字段
 * @param {string} id - 标准字段ID
 * @returns {Promise}
 */
export function getStandardField(id) {
    return get(`/system/standard-fields/${id}`)
}

/**
 * 分页查询标准字段列表
 * @param {Object} params - 分页参数
 * @param {number} params.limit - 每页数量（默认100）
 * @param {number} params.offset - 偏移量（默认0）
 * @returns {Promise}
 */
export function listStandardFields({ limit = 100, offset = 0 } = {}) {
    return get('/system/standard-fields', { limit, offset })
}

// ==================== 标准方法管理 ====================

/**
 * 创建标准方法
 * @param {Object} data - 标准方法数据
 * @returns {Promise}
 */
export function createStandardMethod(data) {
    return post('/system/standard-methods', data)
}

/**
 * 更新标准方法
 * @param {string} id - 标准方法ID
 * @param {Object} data - 要更新的字段
 * @returns {Promise}
 */
export function updateStandardMethod(id, data) {
    return put(`/system/standard-methods/${id}`, data)
}

/**
 * 删除标准方法
 * @param {string} id - 标准方法ID
 * @returns {Promise}
 */
export function deleteStandardMethod(id) {
    return del(`/system/standard-methods/${id}`)
}

/**
 * 查询单个标准方法
 * @param {string} id - 标准方法ID
 * @returns {Promise}
 */
export function getStandardMethod(id) {
    return get(`/system/standard-methods/${id}`)
}

/**
 * 分页查询标准方法列表
 * @param {Object} params - 分页参数
 * @param {number} params.limit - 每页数量（默认100）
 * @param {number} params.offset - 偏移量（默认0）
 * @returns {Promise}
 */
export function listStandardMethods({ limit = 100, offset = 0 } = {}) {
    return get('/system/standard-methods', { limit, offset })
}






// ==================== 版本管理 ====================

/**
 * 获取所有版本列表
 * @returns {Promise}
 */
export function listVersions() {
    return get('/system/versions')
}

/**
 * 获取默认版本
 * @returns {Promise}
 */
export function getDefaultVersion() {
    return get('/system/versions/default')
}

/**
 * 创建版本
 * @param {Object} data - 版本数据
 * @param {string} data.version_code - 版本代码
 * @param {string} data.version_name - 版本名称
 * @param {string} [data.description] - 版本描述
 * @param {string} [data.icon] - 版本图标
 * @param {number} [data.sort_order] - 排序顺序
 * @param {boolean} [data.is_active] - 是否启用
 * @param {boolean} [data.is_default] - 是否默认版本
 * @returns {Promise}
 */
export function createVersion(data) {
    return post('/system/versions', data)
}

/**
 * 更新版本
 * @param {string} versionCode - 版本代码
 * @param {Object} data - 要更新的字段
 * @returns {Promise}
 */
export function updateVersion(versionCode, data) {
    return put(`/system/versions/${versionCode}`, data)
}

/**
 * 删除版本
 * @param {string} versionCode - 版本代码
 * @returns {Promise}
 */
export function deleteVersion(versionCode) {
    return del(`/system/versions/${versionCode}`)
}

// ==================== 菜单配置接口（前端核心接口） ====================

/**
 * 获取版本的菜单配置（前端使用）
 * @param {string} versionCode - 版本代码 (lite, professional, enterprise, ai_edition)
 * @returns {Promise} 返回菜单树结构
 */
export function getMenuConfig(versionCode) {
    return get(`/system/menu/config/${versionCode}`)
}

// ==================== 菜单管理接口（管理员后台使用） ====================

/**
 * 获取所有菜单树（管理用）
 * @returns {Promise} 返回完整的菜单树结构
 */
export function getMenuTree() {
    return get('/system/menus')
}

/**
 * 获取单个菜单详情
 * @param {number} menuId - 菜单ID
 * @returns {Promise}
 */
export function getMenu(menuId) {
    return get(`/system/menus/${menuId}`)
}

/**
 * 创建菜单
 * @param {Object} data - 菜单数据
 * @param {number} [data.parent_id] - 父菜单ID，默认0
 * @param {string} data.menu_path - 菜单路径（唯一）
 * @param {string} data.menu_title - 菜单标题
 * @param {string} [data.menu_icon] - 图标名称
 * @param {string} [data.menu_type] - 菜单类型: menu/container
 * @param {boolean} [data.has_children] - 是否有子菜单
 * @param {string} [data.redirect_path] - 重定向路径
 * @param {number} [data.sort_order] - 排序顺序
 * @param {boolean} [data.is_visible] - 是否可见
 * @returns {Promise}
 */
export function createMenu(data) {
    return post('/system/menus', data)
}

/**
 * 更新菜单
 * @param {number} menuId - 菜单ID
 * @param {Object} data - 要更新的字段
 * @returns {Promise}
 */
export function updateMenu(menuId, data) {
    return put(`/system/menus/${menuId}`, data)
}

/**
 * 删除菜单
 * @param {number} menuId - 菜单ID
 * @returns {Promise}
 */
export function deleteMenu(menuId) {
    return del(`/system/menus/${menuId}`)
}

// ==================== 版本菜单配置管理接口 ====================

/**
 * 获取版本的所有菜单配置（管理用）
 * @param {string} versionCode - 版本代码
 * @returns {Promise} 返回版本的完整菜单配置
 */
export function getVersionMenus(versionCode) {
    return get(`/system/version-menus/${versionCode}`)
}

/**
 * 更新版本下某个菜单的配置
 * @param {string} versionCode - 版本代码
 * @param {number} menuId - 菜单ID
 * @param {Object} data - 配置数据
 * @param {boolean} data.is_visible - 是否可见
 * @param {number} [data.sort_order] - 排序顺序
 * @returns {Promise}
 */
export function updateVersionMenu(versionCode, menuId, data) {
    return put(`/system/version-menus/${versionCode}/menus/${menuId}`, data)
}

/**
 * 批量更新版本菜单配置
 * @param {string} versionCode - 版本代码
 * @param {Array} menus - 菜单配置数组
 * @param {number} menus[].menu_id - 菜单ID
 * @param {boolean} menus[].is_visible - 是否可见
 * @param {number} [menus[].sort_order] - 排序顺序
 * @returns {Promise}
 */
export function batchUpdateVersionMenus(versionCode, menus) {
    return post(`/system/version-menus/${versionCode}/batch`, { menus })
}

/**
 * 初始化版本的菜单配置
 * @param {string} versionCode - 版本代码
 * @returns {Promise}
 */
export function initVersionMenus(versionCode) {
    return post(`/system/version-menus/${versionCode}/init`)
}

/**
 * 复制菜单配置
 * @param {string} fromVersion - 源版本代码
 * @param {string} toVersion - 目标版本代码
 * @returns {Promise}
 */
export function copyMenuConfig(fromVersion, toVersion) {
    return post(`/system/version-menus/copy?from_version=${fromVersion}&to_version=${toVersion}`)
}

// ==================== 测试接口 ====================

/**
 * 测试接口（用于调试）
 * @returns {Promise}
 */
export function testApi() {
    return get('/system/test')
}