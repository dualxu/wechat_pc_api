# Python调用介绍

实际上对[dll接口](dll.md)进行封装， 具体的json参数可以看[API文档](https://www.showdoc.com.cn/579570325733136)

# 快速上手

```python
from __future__ import unicode_literals

import wechat
import json
import time
from wechat import WeChatManager, MessageType

wechat_manager = WeChatManager(libs_path='./libs')


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
            wechat_manager.send_text(client_id, 'filehelper', '😂😂😂\uE052该消息通过python api接口发送')


if __name__ == "__main__":
    bot = LoginTipBot()

    # 添加回调实例对象
    wechat_manager.add_callback_handler(bot)
    wechat_manager.manager_wechat(smart=True)

    # 阻塞主线程
    while True:
        time.sleep(0.5)
```

# 启动微信接口

- 获取用户电脑上安装的微信版本号： WeChatManager.get_user_wechat_version
- 智能管理（启动/多开）企业程序： WeChatManager.manager_wechat
- 通过进程号管理微信： WeChatManager.manager_wechat_by_pid
- 释放所有： WeChatManager.close_manager

# 发送接口

- 发送文本消息： WeChatManager.send_text 
- 发送图片消息： WeChatManager.send_image
- 发送文件消息： WeChatManager.send_file
- 发送链接消息： WeChatManager.send_link
- 发送视频消息： WeChatManager.send_video
- 发送群@消息： WeChatManager.send_chatroom_at_msg
- 发送名片消息：WeChatManager.send_user_card
- 发送gif表情消息： WeChatManager.send_gif
- 获取所有好友： WeChatManager.get_friends
- 获取所有群组： WeChatManager.get_chatroom_members
- 获取指定群成员： WeChatManager.get_chatroom_members
- 获取所有公众号： WeChatManager.get_publics




