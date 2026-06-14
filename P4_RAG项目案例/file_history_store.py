import os
import json
from typing import Sequence
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

#调用get_history函数可以获得到存储实例
#从存储实例调用add_message去添加消息或者调用messages去获取已经存在的消息
def get_history(session_id):
    return FileChatMessageHistory(session_id, "/chat_history")

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        self.session_id = session_id            #会话id
        self.storage_path = storage_path        #不同会话id的存储文件，所在的文件夹路径
        #完整的文件路径
        self.file_path = os.path.join(self.storage_path, self.session_id)

        #确保文件夹是存在的
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    #从存储实例调用add_message去添加消息
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        #Sequence序列 类似list、tuple
        all_messages = list(self.messages)                # 已有的消息列表
        all_messages.extend(messages)                     # 新的和已有的融入成一个list

        #将数据同步写入到本地文件中
        #类对象写入文件 -> 一堆二进制
        #为了方便，可以将BaseMessage消息转为字典（借助json模块以json字符串写入文件）
        #官方message_to_dict: 单个消息对象（BaseMessage类实例）-> 字典
        #new_messages = []
        #for message in all_messages:
        #    d = message_to_dict(message)
        #    new_messages.append(d)

        new_messages = [message_to_dict(message) for message in all_messages]
        #将数据写入文件
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(new_messages, f)

    #从存储实例调用messages去获取已经存在的消息
    @property          #property装饰器将messages方法变为成员属性用
    def messages(self) -> list[BaseMessage]:
        #当前文件内 ：list[字典]
        try:
            with open(self.file_path, "r", encoding='utf-8') as f:
                messages_data = json.load(f)            #返回值就是：list[字典]
                return messages_from_dict(messages_data)          #messages_from_dict：[字典、字典...] -> [消息、消息...]
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
