# ✨️ 概述

`IDEPY Next`是一个专注于Windows桌面应用开发Python框架，基于pywebview深度定制。

它让你能够使用JavaScript、HTML和CSS为Python程序构建现代化GUI，具有Python风格的数据管理和事件绑定功能，实现高效、简洁且功能丰富的桌面应用开发体验。


* 它继承了 Web 技术构建 GUI 的灵活性
* 它大幅扩展了工程能力和 Windows 桌面生态集成功能，降低开发门槛，提升项目稳定性与易用性
* 增加了数据管理API和事件绑定语法糖，jinjia2模板，使开发更符合Python GUI的习惯，显著提升开发效率
* 实现了工程化支持，提供了一套包含Vue、JQuery、Layui、BootStrap、ElementPlus的现代化模板，极大简化了项目入门和开发流程

---
官方文档：[https://idepy.com](https://idepy.com/document/idepy-next-docs)

项目地址：[Github](http://github.com/maplesunrise/idepy-next/) 

支持系统：Windows

python 版本：3.8 及以上

---

`IDEPY Next`包含以下特性
* JavaScript 与 Python 的双向通信以及DOM支持，并提供一套事件语法糖，简单调用 Javascript 事件，绑定回调到Python。
* 内置工程化项目模板，支持原生 JS、Vue、Layui、ElementUI、Bootstrap 等现代化前端框架，开箱即用。
* 提供了高级功能如窗口操作、事件系统、内置HTTP服务器、原生GUI元素（如应用菜单和各种对话框）。
* jinjia2支持，可以使用模板、变量等功能，提高项目代码复用率。
* 集成了桌面开发常见生态功能，托盘菜单、快捷键、配置项、开机启动等。
* cli接口，支持快速创建项目、新建窗口、预览开发情况、一键发布程序并署名信息，无需繁琐配置。
* 专注于 Windows 桌面应用生态优化，使用 Webview2 内核，拥有更佳的程序开发效果。
* 支持 Drissionpage、Playwright等自动化框架进行调试，同时支持为每个窗口设置单独的 storage_path ，同时测试多个窗口。

下面是一个最基本事件绑定示例：
```html
<input id="input1" />
```
```python
@bindElementEvent('#input1', ElementEvent.Input.change)
def input_change(self, *args, **kwargs):
    print("原生输入框输入内容被改变", args)
```
上面示例展现了**事件语法糖**功能：开发者无需编写复杂的JavaScript代码，一句语法糖即可完成事件的绑定，并且支持多个事件同时绑定。

## 适配场景
基于 Python 和 Web 生态特性，IDEPY NEXT框架能适配丰富的开发场景，以下列举部分常见场景：
* 开发精美的GUI：利用 Web 技术构建精致的界面效果；
* Office/文档自动处理工具：Python强大的文档处理库（如python-docx、openpyxl），使用桌面GUI提供便捷的用户交互界面。
* 网页数据导出软件、网页脚本工具：IDEPY Next 支持与 DrissionPage、Playwright 等自动化框架无缝集成，便于构建基于浏览器的爬虫与自动化脚本；
* 网站功能拓展程序：利用API，像浏览器插件一样为网站提供拓展功能；
* 账号管理工具：利用不同的 storage_path 设定，快速切换账号，无需关注具体鉴权信息，轻松开发多账号自动化测试软件。
* AI桌面应用：利用Python丰富的功能生态，集成相关应用，并为其提供桌面的GUI。
* ERP、MES软件开发：IDEPY Next 提供了强大的前端支持（Vue、ElementUI、Bootstrap 等），可快速构建业务表单、报表、流程图等复杂页面；
* 数据可视化与监控仪表盘：支持Jinja2模板、现代前端框架（Vue、Bootstrap等），易于构建美观的图表页面。
* 硬件控制面板/串口通信工具：Python擅长串口、设备通讯； 利用前端构建交互界面，使设备控制更直观。
* ....

## 安装
通常可以通过以下命令安装IDEPY NEXT框架。
```bash
pip install idepy-next
```

## 免责声明
* 本项目允许合法且合规的商业用途，使用者在进行商业使用时必须遵守本声明及相关法律法规。
* 禁止将本项目应用于任何可能违反当地法律法规或道德规范的项目。
* 禁止将本项目用于任何可能损害他人利益的用途。
* 使用本项目所产生的一切行为及其后果由使用者自行承担。因使用本项目导致的任何纠纷、损失或责任，版权持有人概不负责。
* 版权持有人不对本项目可能存在的缺陷或问题所引起的任何直接或间接损失承担责任。





