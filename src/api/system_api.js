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