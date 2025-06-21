import {useIdepyNextVueFramework, initIdepyApp } from "../../lib/idepy_vue/idepy_vue.js"
const {createApp, ref, watch } = Vue

// 创建当前页面Vue实例
const app = createApp({
    setup() {
        // 返回框架对象
        const idepy_vue = useIdepyNextVueFramework()


        // 调用框架设置数据初始值
        idepy_vue.rData.value = {
            version:""
        }




        // 在这里编写你的其他业务逻辑...


        return {
            // 导出框架基本方法
            ...idepy_vue
        }
    }
})

// 初始化，挂载到对应的元素
initIdepyApp(app, "#app")