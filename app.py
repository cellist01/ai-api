import streamlit as st
import requests
from datetime import datetime

# 다른 코드 실행 전에 session_state 초기화
def initialize_state():
    st.session_state.setdefault('messages', [])

# 메인 앱 시작 전에 초기화 실행
initialize_state()

# 메인 타이틀
st.title("AI 챗봇")

# 채팅 이력 표시
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state['messages'].append({
        "role": "user",
        "content": prompt
    })
    
    # AI 응답
    try:
        response = requests.post(
            "https://model.odyssey-ai.svc.cluster.local/v1/completions",
            json={
                "model": "model",
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.7
            },
            verify=False
        )
        ai_response = response.json()["choices"][0]["text"]
        
        # AI 메시지 추가
        st.session_state['messages'].append({
            "role": "assistant",
            "content": ai_response
        })
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    st.rerun()
