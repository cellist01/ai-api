import streamlit as st
import requests
import json
from datetime import datetime

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
        return "죄송합니다. 응답을 생성하는데 문제가 발생했습니다."
    except Exception as e:
        return f"Error: {str(e)}"

def initialize_chat_history():
    """채팅 기록 초기화"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def add_message(role, content):
    """채팅 메시지 추가"""
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": role, "content": content, "time": timestamp})

def main():
    st.title("AI 챗봇")
    
    # 사이드바 설정
    st.sidebar.title("설정")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
    
    # 채팅 기록 초기화
    initialize_chat_history()
    
    # 채팅 기록 표시
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(f"{message['content']}")
                    st.caption(f"sent at {message['time']}")
            else:
                with st.chat_message("assistant"):
                    st.write(f"{message['content']}")
                    st.caption(f"received at {message['time']}")
    
    # 사용자 입력
    user_input = st.chat_input("메시지를 입력하세요...")
    
    if user_input:
        # 사용자 메시지 추가
        add_message("user", user_input)
        
        # AI 응답 생성
        response = call_llm_api(user_input)
        add_message("assistant", response)
        
        # 화면 갱신
        st.rerun()

if __name__ == "__main__":
    main()
