import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd
import time

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
        max-width: 80%;
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
    .error-message {
        color: #f44336;
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'error_count' not in st.session_state:
        st.session_state['error_count'] = 0
    if 'last_timestamps' not in st.session_state:
        st.session_state['last_timestamps'] = []

def call_llm_api(prompt, temperature=0.7, max_tokens=512):
    """LLM API 호출 함수"""
    try:
        response = requests.post(
            API_URL,
            json={
                "model": "model",
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            },
            verify=False,
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()["choices"][0]["text"].strip(), None
    except requests.Timeout:
        return None, "응답 시간이 초과되었습니다."
    except requests.RequestException as e:
        return None, f"API 호출 중 오류가 발생했습니다: {str(e)}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return None, f"응답 처리 중 오류가 발생했습니다: {str(e)}"

def add_message(role, content):
    """메시지 추가 함수"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['messages'].append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })
    
    # 메시지 수 제한
    if len(st.session_state['messages']) > MAX_MESSAGES:
        st.session_state['messages'] = st.session_state['messages'][-MAX_MESSAGES:]

def export_chat_history():
    """대화 내역 내보내기"""
    if not st.session_state['messages']:
        st.sidebar.warning("내보낼 대화 내역이 없습니다.")
        return
    
    df = pd.DataFrame(st.session_state['messages'])
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="대화 내역 다운로드 (CSV)",
        data=csv,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def display_chat_messages():
    """채팅 메시지 표시"""
    for msg in st.session_state['messages']:
        message_container = st.container()
        with message_container:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message user-message">
                        {msg["content"]}
                        <div class="message-timestamp">{msg["timestamp"]}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message assistant-message">
                        {msg["content"]}
                        <div class="message-timestamp">{msg["timestamp"]}</div>
                    </div>
                """, unsafe_allow_html=True)

def main():
    # 세션 초기화
    initialize_session_state()
    
    # 사이드바 설정
    st.sidebar.title("설정")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.sidebar.slider("Max Tokens", 50, 1000, 512)
    
    if st.sidebar.button("대화 초기화"):
        st.session_state['messages'] = []
        st.session_state['error_count'] = 0
        st.rerun()
    
    # 대화 내역 내보내기 버튼
    export_chat_history()
    
    # 메인 화면
    st.title("AI 챗봇 🤖")
    
    # 채팅 이력 표시
    display_chat_messages()
    
    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 추가
        add_message("user", prompt)
        
        # AI 응답 생성
        with st.spinner("AI가 응답을 생성하고 있습니다..."):
            response, error = call_llm_api(prompt, temperature, max_tokens)
            
            if error:
                st.session_state['error_count'] += 1
                st.error(error)
                if st.session_state['error_count'] >= 3:
                    st.warning("여러 번의 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                    time.sleep(5)
            else:
                st.session_state['error_count'] = 0
                add_message("assistant", response)
                st.rerun()

if __name__ == "__main__":
    main()
