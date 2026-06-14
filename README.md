## 🤖 项目名称：基于 LangChain + Qwen3-Max 的电商智能客服与 RAG 尺码推荐系统

## 🎯 业务痛点与解决方案
### 1. 离线知识流：MD5 内容指纹防膨胀
* **痛点**：商家频繁上传、更新相同或微调的尺码文档，导致向量数据库（Chroma）产生大量垃圾分块，检索命中率下降。
* **解法**：引入 hashlib.md5 指纹层。文档进入清洗器前，计算全文本哈希值并动态维护本地 md5.text 清单。遇到重复内容直接执行 [跳过] ，**从源头过滤了 100% 的冗余向量计算与存储空间**。

### 2. 在线检索流：LCEL 弹性装配与幻觉抑制
* **痛点**：大模型在面对“178cm/155斤推荐什么尺码”这类区间数值时，常因过度泛化而瞎编尺码（幻觉）。
* **解法**：使用 LangChain 的 **LCEL（LangChain Expression Language）** 显式编排数据路由。利用 RunnableLambda 动态提取用户意图、注入上下文。在 Prompt 层通过 System 级最高权重强约束大模型“仅依据参考资料回答”。配合自定义 print_prompt 拦截调试链，确保数值回答绝对精准。

### 3. 前端交互流：Generator 异步解耦实现真流式输出
* **痛点**：传统的 .invoke() 会让前端长时期陷入阻塞等待（Loading），随后文本一整块吐出，体验生硬。
* **解法**：采用 .stream() 替代同步阻塞，并在 app_qa.py 中自主设计了 capture() 生成器代理函数。**利用 Python 的 yield 机制，在实时向前端推送 Token 打字机动画的同时，在后台异步完成多轮对话上下文的历史拼接**，完美兼顾了交互体验与数据留存。

### 4. 存储架构：组件解耦与自定义存储逆向修复
* **痛点**：长会话在高并发下状态极易丢失，而原生存储组件在处理 Pydantic 消息模型时常因底层解包引发元组报错崩溃。
* **解法**：通过复写重构 BaseChatMessageHistory 的批量 add_messages 接口，隔离了序列化过程中的元组拆解 bug，实现会话以轻量化 JSON 树稳定持久化于本地本地 chat_history/。

## 🚀 快速开始
### 1. 克隆项目与环境准备
git clone [https://github.com/你的用户名/你的仓库名.git]
                   (https://github.com/你的用户名/你的仓库名.git)                       cd 你的仓库名
                 pip install -r requirements.txt
(注：依赖主要包括 streamlit, langchain, langchain-chroma, dashscope 等)
### 2. 配置环境变量
在系统环境或项目根目录下配置你的阿里百炼平台 API Key：
export DASHSCOPE_API_KEY="your-api-key-here"
### 3. 运行离线知识库上传端
streamlit run app_file_uploader.py
打开浏览器显示的网页，上传您的尺码规范或业务指南 TXT 文件，提示 [成功]内容已经成功载入向量库。
### 4. 启动智能客服对话端
streamlit run app_qa.py
现在您可以向您的智能导购发起多轮对话测试了！

## 🛠️ 技术栈 (Tech Stack)
**前端与交互层 (Frontend & UI)**
* ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=Streamlit&logoColor=white) 核心 Web 框架，实现双端（知识库管理 + 智能问答）流式交互
* **Generator (生成器)**: Python 原生特性，处理流式 Token 渲染防阻塞

**AI 与大模型编排层 (AI & Orchestration)**
* ![LangChain](https://img.shields.io/badge/LangChain-FFFFFF?style=flat-square&logo=langchain&logoColor=black) 核心应用框架，采用 **LCEL (LangChain Expression Language)** 进行链式编排
* **Qwen3-Max (通义千问)**: 核心对话大语言模型（LLM），负责意图理解与内容生成
* **DashScope Embeddings (text-embedding-v4)**: 阿里百炼文本向量化模型

**数据与存储层 (Data & Storage)**
* ![Chroma](https://img.shields.io/badge/ChromaDB-F37F58?style=flat-square) 本地轻量级向量数据库，用于高维语义检索
* **SQLite3**: 存储 Chroma 文档元数据（Metadata）
* **JSON 持久化**: 自定义文件系统方案，稳定存储多轮历史会话

**核心工程化组件 (Engineering Utilities)**
* **RecursiveCharacterTextSplitter**: LangChain 智能文本切片器
* **Hashlib (MD5)**: 内容指纹校验，实现知识库零冗余拦截
