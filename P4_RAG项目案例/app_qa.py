import time
from rag import RagService
import streamlit as st
import config_data as config

# 标题
st.title("智能客服")
st.divider()            #分隔符

#多条历史对话记录->列表[]
#第一次执行看看有没有message，没有的话整一个messaage
if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，有什么可以帮助你？" }]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

#页面刷新后显示历史纪录
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

#在页面最下方提供用户输入栏
prompt = st.chat_input()

if prompt:

    #在页面输出用户的回答
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content":prompt})
    #把消息加载到历史记录里面
    ai_res_list = []
    with st.spinner("AI思考中..."):
        # res_stream本质上是一个迭代器   yield表达式->返回迭代器
        res_stream = st.session_state["rag"].chain.stream({"input":prompt}, config.session_config)
        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk
        st.chat_message("assistant").write_stream(capture(res_stream, ai_res_list))
        #这样页面能按照流水的形式去加载内容了
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})
        # 用空字符串连接 eg.["a","b","c"]    "".join(list) -> abc
        #["a","b","c"]    ",".join(list) -> a,b,c

