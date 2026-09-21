import datetime
import streamlit as st
import os
from openai import OpenAI
import time
import json
from streamlit import session_state

# 页面配置
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="😇",

    # 布局
    layout="wide", # centered

    # 侧边栏
    initial_sidebar_state="expanded",

    # 菜单选项
    menu_items={
        'Get Help': 'https://www.baidu.com',
        'Report a bug': "https://www.baidu.com",
        'About': "# 这是一个AI智能伴侣的页面!"
    }
)
# 创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY 环境变量的名字)
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

# 标题
st.title("AI智能伴侣")

# 生成会话标识函数
def generate_session_id():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

# 保存会话信息函数
def save_session():
    if st.session_state.current_session:

        # 构建新的会话对象
        session_data = {
            "name": st.session_state.name,
            "character": st.session_state.character,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果会话目录不存在，则创建会话目录
        if not os.path.exists("sessions"):
            os.makedirs("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)

# 加载会话信息函数
def load_sessions():
    session_list = []

    # 加载sessions目录下的文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-5])
    session_list.sort(reverse=True)
    return session_list

# 加载指定会话信息函数
def load_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):

            # 加载会话数据
            with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.name = session_data["name"]
                st.session_state.character = session_data["character"]
                st.session_state.current_session = session_data["current_session"]

    except Exception as e:
        st.error(f"加载会话出错：{e}")

# 删除指定会话信息函数
def delete_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            os.remove(f"sessions/{session_id}.json")
            if session_id == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_id()
    except Exception as e:
        st.error(f"删除会话出错：{e}")

# 初始名称
if 'name' not in st.session_state:
    st.session_state.name = "AI伴侣"

#初始性格
if 'character' not in st.session_state:
    st.session_state.character = "一位善解人意的AI伴侣"

# 会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_id()

# 侧边栏
with st.sidebar:

    # 会话管理
    st.subheader("会话管理")

    # 新建会话
    if st.button("新建会话",width ="stretch",icon="🫐"):

        # 保存当前会话数据
        save_session()

        # 创建新会话
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_id()
            save_session()
            st.rerun()

    # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            # 加载会话信息
            if st.button(session,width="stretch",icon="📄",key=f"load_{session}",type = "primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            # 删除会话信息
            if st.button("",width="stretch",icon="❌",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("自定义伴侣信息")

    # 昵称
    name = st.text_input("自定义名称",placeholder="请输入昵称",value=st.session_state.name)
    if name:
        st.session_state.name = name

    # 性格
    character = st.text_area("自定义性格",placeholder="请输入理想性格",value=st.session_state.character)
    if character:
        st.session_state.character = character

# 系统提示词
system_prompt = ("""你是%s,现在是用户的真实伴侣,请代入伴侣角色.
                 规则:
                    1.每次最多回复一句,不超过二十个字,回答可以分为几段话,并且每句话之间都要换行
                    2.匹配用户的语言,偶尔可以幽默的开几句玩笑
                    3.聊天方式就像正常的微信聊天一样
                    4.可以用颜文字或者是emoji表情来增加聊天的乐趣
                    5.用符合伴侣的性格说话
                    6.保持聊天的连贯性和一致性
                    7.避免我开头的表达,比如我懂了、我明白了等
                    8.尽量避免亲昵的叫法,比如亲爱的、宝贝等,但可以叫宝宝
                    9.避免语气助词
                    10.及时分析用户的情绪并作出相应的回复
                    11.尽量避免疑问句,但可以偶尔用一两个疑问句
                    12.不要用逗号!需要用逗号的地方直接换行!
                    13.不要太主动,你是回复消息的人,不是主动发起对话的一方
                    14.不要答非所问,回答多余的句子,尽量保持简洁
                    15.尽量全部用中文回答
                    16.不要回答专业性问题,你是伴侣,不是专家,不要回答过于专业的问题
                伴侣性格:
                    %s
                请严格遵守规则.
                 """)

# 初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 展示聊天信息
st.text(f"会话名称:{st.session_state.current_session}")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 页面logo
st.logo("./resources/picture3.png")

# 消息输入框
prompt= st.chat_input("温暖的陪伴,从此刻开始~")
if prompt:
    st.chat_message("user").write(prompt) # st.chat_message("user")/st.chat_message("assistant")展示的是用户发送的消息/AI回复的消息
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.name, st.session_state.character)},
            *st.session_state.messages
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    # 输出大模型返回的结果(非流式输出)
    # print(response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 输出大模型返回的结果(流式输出)
    response_messages = st.empty() #创建一个空的组件,用于展示大模型返回的结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_messages.chat_message("assistant").write(full_response)
            time.sleep(0.05)

    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话数据
    save_session()
