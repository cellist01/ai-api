import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="AI 챗봇",
    page_icon="🤖",
    layout="wide"
)

# 상수 정의
MAX_MESSAGES = 50
API_TIMEOUT = 30
API_URL = "https://model.odyssey-ai.svc.cluster.local/v1/completions"

# 스타일 설정
st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .message-timestamp {
        color: #666;
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'processing' not in st.session_state:
    st.session_state['processing'] = False

def call_llm_api(prompt):
    """LLM API 호출"""
    try:
        response = requests.post(
            API_URL,
            json={
                "model": "model",
                "prompt": prompt,
                "max_tokens": 256,        # 충분한 컨텍스트 제공
                "temperature": 0.3,       # 낮은 무작위성으로 일관된 응답
                "top_p": 0.9,            # 높은 확률의 토큰만 선택
                "presence_penalty": 0.1,  # 약간의 새로운 정보 추가
                "frequency_penalty": 0.3, # 단어 반복 감소
                "stop": ["\n\n"],        # 명확한 응답 구분
                "n": 1,
            },
            verify=False,
            timeout=API_TIMEOUT
        )
        return response.json()["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# 메인 화면
st.title("AI 챗봇")

# 채팅 이력 표시
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.caption(f"{message['timestamp']}")

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    if not st.session_state['processing']:  # 처리 중이 아닐 때만 실행
        st.session_state['processing'] = True  # 처리 시작
        
        # 사용자 메시지 표시 및 저장
        with st.chat_message("user"):
            st.markdown(prompt)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.caption(timestamp)
        
        st.session_state['messages'].append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })

        # AI 응답 처리
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                response = call_llm_api(prompt)
                st.markdown(response)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.caption(timestamp)
        
        st.session_state['messages'].append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })
        
        # 메시지 수 제한
        if len(st.session_state['messages']) > MAX_MESSAGES:
            st.session_state['messages'] = st.session_state['messages'][-MAX_MESSAGES:]
        
        st.session_state['processing'] = False  # 처리 완료

# 사이드바
with st.sidebar:
    st.title("설정")
    
    # 대화 초기화 버튼
    if st.button("대화 초기화"):
        st.session_state['messages'] = []
        st.rerun()
    
    # 대화 내보내기
    if st.session_state['messages']:
        df = pd.DataFrame(st.session_state['messages'])
        csv = df.to_csv(index=False)
        st.download_button(
            label="대화 내역 다운로드",
            data=csv,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
