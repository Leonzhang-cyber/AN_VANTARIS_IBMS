import { createI18n } from 'vue-i18n'

const messages = {
    en: {
        menu: {
            dashboard: 'Dashboard',
            device: 'Device',
            energy:'Energy',
            alarm:'Alarm',
            maintain:'Maintain',
            report:'Report',
            settings:'Settings',
            carbon: 'Carbon Credit'
        },
        dashboard: 'Dashboard',
        deviceTotal: 'Total Devices',
        deviceOnline: 'Online Devices',
        energyConsumption: 'Energy Consumption',
        alarm: 'Alarm Count',
        energyTrend: 'Energy Trend (24h)',
        deviceList: 'Device List',
        deviceName: 'Device Name',
        status: 'Status',
        createTime: 'Create Time',
    },
    zh: {
        dashboard: '数据概览',
        deviceTotal: '设备总数',
        deviceOnline: '在线设备',
        energyConsumption: '今日能耗',
        alarm: '告警数量',
        energyTrend: '能耗趋势（24小时）',
        deviceList: '设备列表',
        deviceName: '设备名称',
        status: '状态',
        createTime: '创建时间',
    }
}

export default createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages
})