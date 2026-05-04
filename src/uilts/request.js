import axios from 'axios'

const service = axios.create({
    baseURL: '/api',
    timeout: 10000
})

// 请求拦截
service.interceptors.request.use(
    config => config,
    error => Promise.reject(error)
)

// 响应拦截
service.interceptors.response.use(
    res => res.data,
    error => Promise.reject(error)
)

export default service