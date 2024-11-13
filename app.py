import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time
import base64

class ChatApp:
    def __init__(self):
        self.initialize_session_state()
        self.setup_sidebar()
        self.setup_styles()
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "error_count" not in st.session_state:
            st.session_state.error_count = 0
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

    def setup_sidebar(self):
        """사이드바 설정"""
        st.sidebar.title("설정")
        st.session_state.temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
        st.session_state.max_tokens = st.sidebar.slider("Max Tokens", 50, 500, 150)
        
        # 대화 내보내기 버튼
        if st.sidebar.button("대화 내보내기"):
            self.export_chat()
        
        # 대화 초기화 버튼
        if st.sidebar.button("대화 초기화"):
            self.clear_chat()

    def setup_styles(self):
        """스타일 설정"""
        st.markdown("""
        <style>
        .user-message {
            background-color: #e6f3ff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .assistant-message {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .timestamp {
            color: #888;
            font-size: 0.8em;
        }
        .error-message {
            color: red;
            background-color: #ffe6e6;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        </style>
        """, unsafe_allow_html=True)

    def call_llm_api(self, prompt):
        """LLM API 호출"""
        url = "https://model.odyssey-ai.svc.cluster.local/v1/completions"
        
        payload = {
            "model": "model",
            "prompt": prompt,
            "max_tokens": st.session_state.max_tokens,
            "temperature": st.session_state.temperature,
            "top_p": 0.95,
            "n": 1,
            "stream": False,
            "stop": ["\n\n"]
        }
        
        try:
            response = requests.post(url, json=payload, verify=False)
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["text"].strip(), None
            return None, "응답 생성 실패"
            
        except Exception as e:
            return None, str(e)

    def add_message(self, role, content):
        """메시지 추가 및 컨텍스트 관리"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {
            "role": role,
            "content": content,
            "time": timestamp
        }
        st.session_state.messages.append(message)
        self.manage_context()

    def manage_context(self):
        """컨텍스트 길이 관리"""
        max_messages = 50  # 최대 메시지 수
        max_context_length = 2000  # 최대 컨텍스트 길이
        
        # 메시지 수 제한
        if len(st.session_state.messages) > max_messages:
            st.session_state.messages = st.session_state.messages[-max_messages:]
        
        # 컨텍스트 길이 제한
        total_length = sum(len(m["content"]) for m in st.session_state.messages)
        while total_length > max_context_length and len(st.session_state.messages) > 1:
            removed_message = st.session_state.messages.pop(0)
            total_length -= len(removed_message["content"])

    def export_chat(self):
        """대화 내용 내보내기"""
        if not st.session_state.messages:
            st.sidebar.warning("내보낼 대화가 없습니다.")
            return
        
        # DataFrame 생성
        df = pd.DataFrame(st.session_state.messages)
        
        # CSV 파일로 변환
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        
        # 다운로드 버튼
        href = f'<a href="data:file/csv;base64,{b64}" download="chat_history.csv">대화 내역 다운로드</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

    def clear_chat(self):
        """대화 내용 초기화"""
        st.session_state.messages = []
        st.session_state.error_count = 0
        st.experimental_rerun()

    def handle_error(self, error):
        """에러 처리"""
        st.session_state.error_count += 1
        st.error(f"오류가 발생했습니다: {str(error)}")
        
        if st.session_state.error_count >= 3:
            st.warning("여러 번의 오류가 발생했습니다. 페이지를 새로고침하시겠습니까?")
            if st.button("새로고침"):
                st.session_state.clear()
                st.experimental_rerun()

    def display_chat_history(self):
        """채팅 기록 표시"""
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='timestamp'>{message['time']}</div>", unsafe_allow_html=True)
            else:
                with st.chat_message("assistant"):
                    st.markdown(f"<div class='assistant-message'>{message['content']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='timestamp'>{message['time']}</div>", unsafe_allow_html=True)

    def run(self):
        """메인 애플리케이션 실행"""
        st.title("AI 챗봇")
        
        # 채팅 기록 표시
        self.display_chat_history()
        
        # 사용자 입력 처리
        user_input = st.chat_input("메시지를 입력하세요...")
        
        if user_input:
            # 사용자 메시지 추가
            self.add_message("user", user_input)
            
            # 로딩 표시
            with st.spinner("AI가 응답을 생성 중입니다..."):
                response, error = self.call_llm_api(user_input)
            
            if error:
                self.handle_error(error)
            else:
                self.add_message("assistant", response)
            
            # 화면 갱신
            st.experimental_rerun()

if __name__ == "__main__":
    app = ChatApp()
    app.run()
