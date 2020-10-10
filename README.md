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
import wxwork
import json
import time
from wxwork import WxWorkManager,MessageType

wxwork_manager = WxWorkManager(libs_path='../../libs')

# 这里测试函数回调
@wxwork.CONNECT_CALLBACK(in_class=False)
def on_connect(client_id):
    print('[on_connect] client_id: {0}'.format(client_id))

@wxwork.RECV_CALLBACK(in_class=False)
def on_recv(client_id, message_type, message_data):
    print('[on_recv] client_id: {0}, message_type: {1}, message:{2}'.format(client_id, 
    message_type, json.dumps(message_data)))

@wxwork.CLOSE_CALLBACK(in_class=False)
def on_close(client_id):
    print('[on_close] client_id: {0}'.format(client_id))


class EchoBot(wxwork.CallbackHandler):


    @wxwork.RECV_CALLBACK(in_class=True)
    def on_message(self, client_id, message_type, message_data):

        # 如果是文本消息，就回复一条消息
        if message_type == MessageType.MT_RECV_TEXT_MSG:
            reply_content = '😂😂😂你发过来的消息是：{0}'.format(message_data['content'])
            time.sleep(2)
            wxwork_manager.send_text(client_id, message_data['conversation_id'], reply_content)


if __name__ == "__main__":
    echoBot = EchoBot()

    # 添加回调实例对象
    wxwork_manager.add_callback_handler(echoBot)
    wxwork_manager.manager_wxwork(smart=True)

    # 阻塞主线程
    while True:
        time.sleep(0.5)

```


帮助&支持
-------------------------
点击链接加入群聊[WeChatApi交流群: 308918346](https://jq.qq.com/?_wv=1027&k=EfM5FKpY)

<img src="./doc/qqgroup.jpg" height="300" />
