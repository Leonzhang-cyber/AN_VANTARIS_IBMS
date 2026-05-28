// src/utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const devUrl = 'http://127.0.0.1:5000/api'
const online = 'https://ibms.aegisnx.com/api'

const BASE_URL =  devUrl // 替换为你的实际后端地址

// https://ibms.aegisnx.com/api
// http://127.0.0.1:5000/api

const service = axios.create({
    baseURL: BASE_URL,
    timeout: 120000
})

// 请求拦截器
service.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers = {
                ...config.headers,
                'Authorization': `Bearer ${token}`
            }
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    (response) => {
        const { status, data } = response

        if (status === 200) {
            if (data.code === 200) {
                return data.data
            } else {
                const msg = data.message || '请求失败'
                ElMessage.error(msg)
                return Promise.reject(new Error(msg))
            }
        } else if (status === 401) {
            localStorage.removeItem('token')
            window.location.href = '/login'
            return Promise.reject(new Error('登录已过期'))
        } else {
            const msg = '网络异常，请稍后重试'
            ElMessage.error(msg)
            return Promise.reject(new Error(msg))
        }
    },
    (error) => {
        const msg = error.message || '网络连接失败'
        ElMessage.error(msg)
        return Promise.reject(error)
    }
)

// 封装请求方法
export const get = (url, params = {}) => {
    return service({
        url,
        method: 'GET',
        params
    })
}

export const post = (url, data = {}) => {
    return service({
        url,
        method: 'POST',
        data
    })
}

export const put = (url, data = {}) => {
    return service({
        url,
        method: 'PUT',
        data
    })
}

export const del = (url, params = {}) => {
    return service({
        url,
        method: 'DELETE',
        params
    })
}

// 添加 patch 方法
export const patch = (url, data = {}) => {
    return service({ url, method: 'PATCH', data })
}

export default service