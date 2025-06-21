const {createApp, ref, watch } = Vue


export function useIdepyNextVueFramework(){
        // Vue3变量创建
        const rData = ref({})

        // 配置项
        const config = ref({})

        // 通过接口刷新当前程序配置项
        function refreshConfigData() {
            idepy.api.get_config_data().then((data) => {
                console.log("[Config]", data)
                config.value = data
                idepy_config_data = data
            })
        }


        // 通过接口程序刷新当前页面数据
        function refreshData() {
            idepy.api.get_data().then((data) => {
                console.log("[data]", data)
                rData.value = data
                idepy_web_data = data
            })
        }


        // 手动通过接口数据将当前页面数据传递到Python
        function updateData() {
            idepy.api.set_web_data(rData?.value)
        }

        let dataWatcher = null
        function startDataWatcher(){
           // 监听器自动更新数据
           watch(()=>rData.value,(newValue,oldValue)=>{
                dataWatcher = idepy?.api?.set_web_data(newValue)
           },{deep:true})

        }

        function stopDataWatcher() {
            dataWatcher()
        }



        // 获取api对象
        const api = ref({})
        const api_interval = setInterval(()=>{
            if (window?.idepy?.api){
                clearInterval(api_interval)
                api.value = window?.idepy?.api;
            }
        }, 333)




        // 暴露相关方法、变量，提供Vue访问
        return {
            rData, refreshData, updateData,
            startDataWatcher,stopDataWatcher,
            config,refreshConfigData,
            window:window,
            api

        }
}


export function initIdepyApp(app, selector="#app") {


    // 挂载element-plus组件库
    app.use(ElementPlus, {
        locale: ElementPlusLocaleZhCn
    });

    // 注册图标组件
    for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
      app.component(key, component)
    }


    // 创建Vue实例
    window.vm = app.mount(selector)


    // 挂载常用方法到全局变量
    window.refreshData = vm.refreshData
    window.refreshConfigData = vm.refreshConfigData
    window.updateData = vm.updateData



    // 窗口创建完毕后将调用逻辑
    window.removeEventListener('idepyready', initIdepy);
    window.addEventListener('idepyready',  () => {
        console.log("[INFO]桌面应用初始化成功")

        // 获取初始数据
        vm.refreshData()
        vm.refreshConfigData()
        vm.startDataWatcher()


    })


}

