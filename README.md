介绍
=============================
wechat_pc_api 使用HOOK技术将核心功能封装成dll，并提供简易的接口给程序调用。

你可以通过扩展 wechat_pc_api 来实现：

* 监控或收集微信消息
* 自动消息推送
* 聊天机器人
* 通过微信远程控制你的设备

测试可以使用语言有C/C++，C#，易语言，Python, Java, Go, NodeJs, PHP, VB, Delphi。

目前支持的微信PC版本是2.8.0.121, 使用api前，先这里下载并安装[WeChatSetup_2.8.0.121.exe](https://pan.baidu.com/s/1Mg4GAzE--Qx9CMLPpvzOLA)  提取码：fg8b


功能清单
-----------------------------------
- 微信多开
- 支持收发所有类型的消息
- 获取全部好友，群，公众号等信息

文档
----------------------------
- [DLL接口介绍](doc/dll.md)
- [API接口参数](https://www.showdoc.com.cn/579570325733136)
- [Python调用介绍](doc/python.md)


具体使用可以暂时参考samples/python/demo.py, 如下是python封装后的调用

```python
from __future__ import unicode_literals

import wechat
import json
import time
from wechat import WeChatManager, MessageType

wechat_manager = WeChatManager(libs_path='../../libs')


# 这里测试函数回调
@wechat.CONNECT_CALLBACK(in_class=False)
def on_connect(client_id):
    print('[on_connect] client_id: {0}'.format(client_id))


@wechat.RECV_CALLBACK(in_class=False)
def on_recv(client_id, message_type, message_data):
    print('[on_recv] client_id: {0}, message_type: {1}, message:{2}'.format(client_id,
                                                                            message_type, json.dumps(message_data)))


@wechat.CLOSE_CALLBACK(in_class=False)
def on_close(client_id):
    print('[on_close] client_id: {0}'.format(client_id))


# 这里测试类回调， 函数回调与类回调可以混合使用
class LoginTipBot(wechat.CallbackHandler):

    @wechat.RECV_CALLBACK(in_class=True)
    def on_message(self, client_id, message_type, message_data):
        # 判断登录成功后，就向文件助手发条消息
        if message_type == MessageType.MT_USER_LOGIN:
            time.sleep(2)
            wechat_manager.send_text(client_id, 'filehelper', '😂😂😂\uE052该消息通过wechat_pc_api项目接口发送')
            
            wechat_manager.send_link(client_id, 
            'filehelper', 
            'wechat_pc_api项目', 
            'WeChatPc机器人项目', 
            'https://github.com/smallevilbeast/wechat_pc_api', 
            'https://www.showdoc.com.cn/server/api/attachment/visitfile/sign/0203e82433363e5ff9c6aa88aa9f1bbe?showdoc=.jpg)')


if __name__ == "__main__":
    bot = LoginTipBot()

    # 添加回调实例对象
    wechat_manager.add_callback_handler(bot)
    wechat_manager.manager_wechat(smart=True)

    # 阻塞主线程
    while True:
        time.sleep(0.5).5)

```


帮助&支持
-------------------------
点击链接加入群聊[WeChatApi交流群: 308918346](https://jq.qq.com/?_wv=1027&k=EfM5FKpY)

<img src="./doc/qqgroup.jpg" height="300" />
