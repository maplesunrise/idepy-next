// 触发beforeAppMounted事件，注册DOM元素
const beforeAppMountedEvent = new CustomEvent('beforeAppMounted', {});
window.dispatchEvent(beforeAppMountedEvent);

function serializeElements(selectors) {
    /**
     序列化页面元素
     **/

  const result = [];

  selectors.forEach(sel => {
    const elements = document.querySelectorAll(sel);

    elements.forEach(el => {
      const tag = el.tagName;
      const type = el.type;

      if (type === 'file') return; // 跳过文件

      let value = null;

      if (tag === 'INPUT') {
        if (type === 'checkbox') {
          value = el.checked;
        } else if (type === 'radio') {
          if (!el.checked) return;
          value = el.value;
        } else {
          value = el.value;
        }
      } else if (tag === 'TEXTAREA') {
        value = el.value;
      } else if (tag === 'SELECT') {
        value = el.multiple
          ? Array.from(el.selectedOptions).map(o => o.value)
          : el.value;
      } else if (el.isContentEditable) {
        value = el.innerText;
      }

      result.push({ selector: sel, value });
    });
  });

  return JSON.stringify(result);
}


function deserializeElements(data_str) {
    /**
     反序列化页面元素
    **/

  let data = JSON.parse(data_str)
  data.forEach(({ selector, value }) => {
    const el = document.querySelector(selector);
    if (!el) return;

    const tag = el.tagName;
    const type = el.type;

    if (tag === 'INPUT') {
      if (type === 'checkbox') {
        el.checked = Boolean(value);
      } else if (type === 'radio') {
        el.checked = el.value === value;
      } else {
        el.value = value;
      }
    } else if (tag === 'TEXTAREA' || tag === 'SELECT') {
      if (el.multiple && Array.isArray(value)) {
        Array.from(el.options).forEach(o => {
          o.selected = value.includes(o.value);
        });
      } else {
        el.value = value;
      }
    } else if (el.isContentEditable) {
      el.innerText = value;
    }
  });
}

// 页面数据
let idepy_web_data = {}

// 页面配置
let idepy_config_data = {}
function idepy_set_web_data(data) {
    /**
    设置页面数据
   **/
  return idepy.api.set_data(data).then((res)=>{
      idepy_web_data = res
  })
}

function idepy_update_web_data(key, value, refresh=true) {
   /**
    更新页面数据
   **/
  return idepy.api.update_web_data(key, value, refresh).then((res)=>{
      idepy_web_data = res
  })
}

function idepy_get_web_data() {
   /**
    获取页面数据
   **/
  return idepy.api.get_data().then((res)=>{
      idepy_web_data = res
  })
}


function idepy_update_config(key, value) {
   /**
    更新配置数据
   **/
  return idepy.api.update_config(key, value).then((res)=>{
      idepy_data = res
  })
}

function idepy_get_config_data() {
   /**
   获取配置数据
   **/
  return idepy.api.get_config_data().then((res)=>{
      idepy_config_data = res
  })
}

function refreshData(){
  /**
   刷新窗口数据
   **/
  idepy_get_web_data()
}

function refreshConfigData(){
  /**
   刷新窗口配置数据
   **/
  idepy_get_config_data()
}



function updateData() {
    /**
   手动通过接口数据将当前页面数据传递到Python
   **/
    idepy_set_web_data(idepy_web_data)
}


function initIdepy(){
    console.log("[INFO]桌面应用初始化成功")

    // 获取初始数据
    refreshData()
    refreshConfigData()
}
// 窗口创建完毕后将调用逻辑
window.addEventListener('idepyready',  initIdepy)