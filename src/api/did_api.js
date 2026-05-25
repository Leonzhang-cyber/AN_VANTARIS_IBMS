// api/did_api.js
/**
 * DID 模块 API 封装
 * 对应后端 Flask 路由 /did/*
 * 使用 @/utils/request 中封装的 get/post 方法
 * 请求自动携带 token（如果存在）
 */

import { get, post } from '@/uilts/request.js'

// ==================== 1. 系统初始化 ====================
/**
 * 初始化系统实体（最高权限根实体），幂等操作
 * @returns {Promise<Object>} { did, public_key, private_key, entity_info, is_new }
 */
export const initSystem = () => {
    return post('/did/system/init')
}

// ==================== 2. 创建下级实体并签发 VC ====================
/**
 * 上级创建下级实体，自动生成密钥对，并签发 VC
 * @param {Object} params
 * @param {string} params.parent_did - 上级 DID
 * @param {string} params.parent_private_key - 上级私钥
 * @param {string} params.entity_type_code - 实体类型代码（如 'property'）
 * @param {string} params.name - 实体名称
 * @param {string[]} params.permissions - 权限列表
 * @param {Object} [params.extra] - 额外信息
 * @param {string} [params.credential_type] - VC 类型，默认 'EntityCredential'
 * @param {Object} [params.custom_claims] - 自定义声明
 * @param {number} [params.valid_days] - 有效期天数
 * @returns {Promise<Object>} { did, private_key, public_key, vc, entity_info }
 */
export const createEntity = (params) => {
    return post('/did/entity', params)
}

// ==================== 3. 用户生成 VP ====================
/**
 * 持有者生成可验证表达 VP
 * @param {Object} params
 * @param {string} params.holder_did - 持有者 DID
 * @param {string} params.holder_private_key - 持有者私钥
 * @param {Array<Object>} params.vcs - VC 列表
 * @param {string} params.challenge - 随机挑战码
 * @param {string} [params.domain] - 域
 * @returns {Promise<Object>} 完整的 VP JSON 对象
 */
export const generateVP = (params) => {
    return post('/did/vp/generate', params)
}

// ==================== 4. 验证 VP 并提取信息 ====================
/**
 * 验证 VP，若通过则返回 VP 中包含的用户信息
 * @param {Object} params
 * @param {Object} params.vp - VP 对象
 * @param {string} params.challenge - 挑战码
 * @returns {Promise<Object>} { valid: boolean, subject_info: Object }
 */
export const verifyVP = (params) => {
    return post('/did/vp/verify', params)
}

// ==================== 5. 吊销并重新签发 VC ====================
/**
 * 吊销原 VC 并重新签发新 VC（保留 DID）
 * @param {Object} params
 * @param {string} params.issuer_did - 签发者 DID
 * @param {string} params.issuer_private_key - 签发者私钥
 * @param {string} params.subject_did - 主体 DID
 * @param {string[]} [params.new_permissions] - 新权限列表
 * @param {Object} [params.new_extra] - 新额外信息
 * @param {string} [params.new_public_key] - 新公钥（可选，不改则忽略）
 * @param {string} [params.credential_type] - VC 类型
 * @param {Object} [params.custom_claims] - 自定义声明
 * @param {string} [params.old_vc_id] - 原 VC ID
 * @returns {Promise<Object>} { did, private_key, public_key, vc, entity_info }
 */
export const revokeAndReissueVC = (params) => {
    return post('/did/vc/reissue', params)
}

// ==================== 6. 撤销 VC ====================
/**
 * 撤销指定的 VC
 * @param {Object} params
 * @param {string} params.vc_id - VC ID
 * @param {string} params.revoked_by_did - 撤销者 DID
 * @returns {Promise<Object>} 成功返回 { message: 'VC撤销成功' }
 */
export const revokeVC = (params) => {
    return post('/did/vc/revoke', params)
}

// ==================== 7. 检查 VC 状态 ====================
/**
 * 检查 VC 是否有效（签名、过期、撤销、签发者/持有者状态）
 * @param {Object} params
 * @param {Object} params.vc - VC 对象
 * @returns {Promise<Object>} { valid: boolean, reason: string, subject_info: Object }
 */
export const checkVCStatus = (params) => {
    return post('/did/vc/status', params)
}

// ==================== 8. 生成挑战码 ====================
/**
 * 生成随机挑战码（用于 VP 防重放或 Challenge-Response 登录）
 * @param {number} [length=32] - 挑战码长度
 * @returns {Promise<Object>} { challenge: string }
 */
export const generateChallenge = (length = 32) => {
    return get('/did/challenge', { length })
}

// ==================== 9. 查询直接下级 ====================
/**
 * 查询直接下级列表
 * @param {string} parent_did - 上级 DID
 * @returns {Promise<Array>} 下级实体列表
 */
export const getDirectSubordinates = (parent_did) => {
    return get('/did/subordinates/direct', { parent_did })
}

// ==================== 10. 查询所有下级树 ====================
/**
 * 查询所有下级及下级的下级，返回树形结构
 * @param {string} parent_did - 上级 DID
 * @returns {Promise<Object>} 树形结构 { did, name, children, ... }
 */
export const getSubordinatesTree = (parent_did) => {
    return get('/did/subordinates/tree', { parent_did })
}

// ==================== 11. 查询所有后代平铺列表 ====================
/**
 * 查询所有后代实体（平铺列表）
 * @param {string} parent_did - 上级 DID
 * @returns {Promise<Array>} 后代实体列表
 */
export const getSubordinatesFlat = (parent_did) => {
    return get('/did/subordinates/flat', { parent_did })
}

// ==================== 12. 查询实体信息 ====================
/**
 * 根据 DID 查询实体完整信息（含链上锚定哈希和交易哈希）
 * @param {string} did - 实体 DID
 * @returns {Promise<Object>} 实体详细信息
 */
export const getEntityInfo = (did) => {
    return get(`/did/entity/${did}`)
}

// ==================== 13. 登录 ====================
/**
 * 登录接口（支持 VP 模式或 Challenge 模式）
 * @param {Object} params
 * - VP 模式: { vp: Object, challenge: string }
 * - Challenge 模式: { did: string, challenge: string, signature: string }
 * @returns {Promise<Object>} { token: string }
 */
export const login = (params) => {
    return post('/did/login', params)
}

// ==================== 14. 获取当前用户信息 ====================
/**
 * 获取当前登录用户的 DID 信息（需携带 JWT Token）
 * @returns {Promise<Object>} 当前实体完整信息
 */
export const getCurrentUserInfo = () => {
    return get('/did/me')
}

// ==================== 15. 查询实体链上哈希 ====================
/**
 * 根据 DID 查询链上存储的实体元数据哈希
 * @param {string} did - 实体 DID
 * @returns {Promise<Object>} { did, metadata_hash }
 */
export const getEntityChainHash = (did) => {
    return get(`/did/chain/entity-hash/${did}`)
}

// ==================== 16. 查询 VC 链上哈希 ====================
/**
 * 根据 VC ID 查询链上存储的 VC 哈希
 * @param {string} vc_id - VC ID
 * @returns {Promise<Object>} { vc_id, vc_hash }
 */
export const getVCChainHash = (vc_id) => {
    return get(`/did/chain/vc-hash/${vc_id}`)
}

// ==================== 17. 获取合约事件记录 ====================
/**
 * 获取锚定合约的历史事件记录（支持按事件名称过滤）
 * @param {Object} [params]
 * @param {string} [params.event_name] - 事件名称，如 'EntityAnchored'
 * @param {number} [params.from_block=0] - 起始区块
 * @returns {Promise<Object>} { events: Array }
 */
export const getContractEvents = (params = {}) => {
    return get('/did/chain/events', params)
}

// ==================== 18. 核对实体信息与链上哈希 ====================
/**
 * 核对实体信息是否与链上锚定哈希一致
 * @param {string} did - 实体 DID
 * @returns {Promise<Object>} { did, verified, local_hash, chain_hash }
 */
export const verifyEntityIntegrity = (did) => {
    return get(`/did/verify/entity/${did}`)
}