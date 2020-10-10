# -*- coding: utf-8 -*-

import json
import sys
import os
import os.path
import inspect
import copy
from functools import wraps
from ctypes import WinDLL, c_ulong, c_char_p, create_string_buffer, WINFUNCTYPE

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WeChatManager')


def is_64bit():
    return sys.maxsize > 2 ** 32


def c_string(data):
    return c_char_p(data.encode('utf-8'))


class MessageType:
    MT_DEBUG_LOG = 11024
    MT_RECV_QRCODE_MSG = 11087

    MT_USER_LOGIN = 11025
    MT_USER_LOGOUT = 11026

    MT_DATA_FRIENDS_MSG = 11030
    MT_DATA_CHATROOMS_MSG = 11031
    MT_DATA_CHATROOM_MEMBERS_MSG = 11032
    MT_DATA_PUBLICS_MSG = 11033

    MT_SEND_TEXTMSG = 11036
    MT_SEND_CHATROOM_ATMSG = 11037
    MT_SEND_CARDMSG = 11038
    MT_SEND_LINKMSG = 11039
    MT_SEND_IMGMSG = 11040
    MT_SEND_FILEMSG = 11041
    MT_SEND_VIDEOMSG = 11042
    MT_SEND_GIFMSG = 11043

    MT_RECV_TEXT_MSG = 11046
    MT_RECV_PICTURE_MSG = 11047
    MT_RECV_VOICE_MSG = 11048
    MT_RECV_FRIEND_MSG = 11049
    MT_RECV_CARD_MSG = 11050
    MT_RECV_VIDEO_MSG = 11051
    MT_RECV_EMOJI_MSG = 11052
    MT_RECV_LOCATION_MSG = 11053
    MT_RECV_LINK_MSG = 11054
    MT_RECV_FILE_MSG = 11055
    MT_RECV_MINIAPP_MSG = 11056
    MT_RECV_WCPAY_MSG = 11057
    MT_RECV_SYSTEM_MSG = 11058
    MT_RECV_REVOKE_MSG = 11059
    MT_RECV_OTHER_MSG = 11060
    MT_RECV_OTHER_APP_MSG = 11061


class CallbackHandler:
    pass


_GLOBAL_CONNECT_CALLBACK_LIST = []
_GLOBAL_RECV_CALLBACK_LIST = []
_GLOBAL_CLOSE_CALLBACK_LIST = []


def CONNECT_CALLBACK(in_class=False):
    def decorator(f):
        wraps(f)
        if in_class:
            f._wx_connect_handled = True
        else:
            _GLOBAL_CONNECT_CALLBACK_LIST.append(f)
        return f

    return decorator


def RECV_CALLBACK(in_class=False):
    def decorator(f):
        wraps(f)
        if in_class:
            f._wx_recv_handled = True
        else:
            _GLOBAL_RECV_CALLBACK_LIST.append(f)
        return f

    return decorator


def CLOSE_CALLBACK(in_class=False):
    def decorator(f):
        wraps(f)
        if in_class:
            f._wx_close_handled = True
        else:
            _GLOBAL_CLOSE_CALLBACK_LIST.append(f)
        return f

    return decorator


def add_callback_handler(callbackHandler):
    for dummy, handler in inspect.getmembers(callbackHandler, callable):
        if hasattr(handler, '_wx_connect_handled'):
            _GLOBAL_CONNECT_CALLBACK_LIST.append(handler)
        elif hasattr(handler, '_wx_recv_handled'):
            _GLOBAL_RECV_CALLBACK_LIST.append(handler)
        elif hasattr(handler, '_wx_close_handled'):
            _GLOBAL_CLOSE_CALLBACK_LIST.append(handler)


@WINFUNCTYPE(None, c_ulong)
def wechat_connect_callback(client_id):
    for func in _GLOBAL_CONNECT_CALLBACK_LIST:
        func(client_id)


@WINFUNCTYPE(None, c_ulong, c_char_p, c_ulong)
def wechat_recv_callback(client_id, data, length):
    data = copy.deepcopy(data)
    json_data = data.decode('utf-8')
    dict_data = json.loads(json_data)
    for func in _GLOBAL_RECV_CALLBACK_LIST:
        func(client_id, dict_data['type'], dict_data['data'])


@WINFUNCTYPE(None, c_ulong)
def wechat_close_callback(client_id):
    for func in _GLOBAL_CLOSE_CALLBACK_LIST:
        func(client_id)


class REQUIRE_WXLOADER:
    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            obj, args = args[0], args[1:]
            if obj.WXLOADER is not None:

                return func(obj, *args, **kwargs)
            else:
                logger.error("wechatApi init failed")

        return wrapper


class WeChatManager:
    # 加载器
    WXLOADER = None

    # wechatHelper.dll
    wxhelper_dll_path = ''

    # 可指定WeChat.exe路径，也可以设置为空
    wechat_exe_path = ''

    def __init__(self, libs_path, wechat_exe_path=''):
        self.wechat_exe_path = wechat_exe_path
        wechat_loader_path = os.path.join(libs_path, 'WxLoader_{0}.dll'.format('x64' if is_64bit() else 'x86'))
        wechat_loader_path = os.path.realpath(wechat_loader_path)

        if not os.path.exists(wechat_loader_path):
            logger.error('libs path error or wechatLoader not exist: %s', wechat_loader_path)
            return

        self.WXLOADER = WinDLL(wechat_loader_path)

        # 使用utf8编码
        self.WXLOADER.UseUtf8()

        # 初始化接口回调
        self.WXLOADER.InitWeChatSocket(wechat_connect_callback, wechat_recv_callback, wechat_close_callback)

        self.wxhelper_dll_path = '{0}/WeChatHelper_{1}.dll'.format(libs_path, self.get_user_wechat_version())
        if not os.path.exists(self.wxhelper_dll_path):
            logger.error('lib file：%s not exist', self.wxhelper_dll_path);
            return

        if wechat_exe_path != '' and not os.path.exists(wechat_exe_path):
            logger.warning('wechat.exe is the path set correctly?')

        self.wechat_exe_path = wechat_exe_path

    def add_callback_handler(self, callback_handler):
        add_callback_handler(callback_handler)

    @REQUIRE_WXLOADER()
    def get_user_wechat_version(self):
        out = create_string_buffer(20)
        self.WXLOADER.GetUserWeChatVersion(out)
        return out.value.decode('utf-8')

    @REQUIRE_WXLOADER()
    def manager_wechat(self, smart=True):
        if smart:
            return self.WXLOADER.InjectWeChat2(c_string(self.wxhelper_dll_path), c_string(self.wechat_exe_path))
        else:
            return self.WXLOADER.InjectWeChatMultiOpen(c_string(self.wxhelper_dll_path), c_string(self.wechat_exe_path))

    @REQUIRE_WXLOADER()
    def manager_wechat_by_pid(self, wechat_pid):
        return self.WXLOADER.InjectWeChatPid(wechat_pid, c_string(self.wxhelper_dll_path))

    @REQUIRE_WXLOADER()
    def close_manager(self):
        return self.WXLOADER.DestroyWeChat()

    @REQUIRE_WXLOADER()
    def send_message(self, client_id, message_type, params):
        send_data = {
            'type': message_type,
            'data': params
        }
        return self.WXLOADER.SendWeChatData(client_id, c_string(json.dumps(send_data)))

    # 发送文本消息
    def send_text(self, client_id, to_wxid, text):
        data = {
            'to_wxid': to_wxid,
            'content': text
        }
        return self.send_message(client_id, MessageType.MT_SEND_TEXTMSG, data)

    # 发送群at消息
    def send_chatroom_at_msg(self, client_id, to_wxid, content, at_list):
        data = { 
            'to_wxid': to_wxid,
            'content': content,
            'at_list': at_list
        }
        return self.send_message(client_id, MessageType.MT_SEND_CHATROOM_ATMSG, data)

    # 发送名片
    def send_user_card(self, client_id, to_wxid, wxid):
        data = { 
            'to_wxid': to_wxid,
            'card_wxid': wxid
        }
        return self.send_message(client_id, MessageType.MT_SEND_CARDMSG, data)

    # 发送链接
    def send_link(self, client_id, to_wxid, title, desc, url, image_url):
        data = {
            'to_wxid': to_wxid,
            'title': title,
            'desc': desc,
            'url': url,
            'image_url': image_url
        }
        return self.send_message(client_id, MessageType.MT_SEND_LINKMSG, data)

    # 发送图片
    def send_image(self, client_id, to_wxid, file):
        data = {
            'to_wxid': to_wxid,
            'file': file
        }
        return self.send_message(client_id, MessageType.MT_SEND_IMGMSG, data)

    # 发送文件
    def send_file(self, client_id, to_wxid, file):
        data = {
            'to_wxid': to_wxid,
            'file': file
        }
        return self.send_message(client_id, MessageType.MT_SEND_FILEMSG, data)  

    # 发送视频
    def send_video(self, client_id, to_wxid, file):
        data = {
            'to_wxid': to_wxid,
            'file': file
        }
        return self.send_message(client_id, MessageType.MT_SEND_VIDEOMSG, data)     

    # 发送gif
    def send_gif(self, client_id, to_wxid, file):
        data = {
            'to_wxid': to_wxid,
            'file': file
        }
        return self.send_message(client_id, MessageType.MT_SEND_GIFMSG, data) 

    # 获取所有联系人
    def get_friends(self, client_id):
        return self.send_message(client_id, MessageType.MT_DATA_FRIENDS_MSG, {})

    # 获取所有群组
    def get_chatrooms(self, client_id):
        return self.send_message(client_id, MessageType.MT_DATA_CHATROOMS_MSG, {})

    # 获取所有群成员
    def get_chatroom_members(self, client_id, room_wxid):
        data = {
            'room_wxid': room_wxid
        }
        return self.send_message(client_id, MessageType.MT_DATA_CHATROOM_MEMBERS_MSG, data)

    # 获取所有公众号
    def get_publics(self, client_id):
        return self.send_message(client_id, MessageType.MT_DATA_PUBLICS_MSG, {})
