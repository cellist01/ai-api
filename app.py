import streamlit as st
import requests
from datetime import datetime

# 기본 페이지 설정
st.set_page_config(
    page_title="AI 챗봇",
    layout="wide"
)

# 초기 상태 설정
if "messages" not in st.session_state:
    st.session_state.messages = []

def call_llm_api(prompt):
    """LLM API 호출"""
    url = "https://model.odyssey-ai.svc.cluster.local/v1/completions"
    payload = {
        "model": "model",
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.95,
        "n": 1,
        "stream": False,
        "stop": ["\n\n"]
    }
    
    try:
        response = requests.post(url, json=payload, verify=False)
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["text"].strip()
        return "응답을 생성할 수 없습니다."
    except Exception as e:
        return f"Error: {str(e)}"

# 메인 UI
st.title("AI 챗봇")

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        st.caption(f"sent at {message['time']}")

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    
    # AI 응답 생성
    with st.spinner("AI가 응답을 생성중입니다..."):
        response = call_llm_api(prompt)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M:%S")
        })
    
    st.experimental_rerun()

# 사이드바 설정
with st.sidebar:
    st.title("설정")
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.experimental_rerun()
