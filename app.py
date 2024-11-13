import streamlit as st
import requests
import json
from datetime import datetime

# 전역 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'error_count' not in st.session_state:
    st.session_state.error_count = 0
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7
if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 150

class ChatApp:
    def __init__(self):
        self.setup_sidebar()
        self.setup_styles()
    
    def setup_sidebar(self):
        """사이드바 설정"""
        st.sidebar.title("설정")
        # session_state 사용
        st.session_state.temperature = st.sidebar.slider("Temperature", 0.0, 1.0, st.session_state.temperature)
        st.session_state.max_tokens = st.sidebar.slider("Max Tokens", 50, 500, st.session_state.max_tokens)
        
        if st.sidebar.button("대화 내보내기"):
            self.export_chat()
        
        if st.sidebar.button("대화 초기화"):
            st.session_state.messages = []
            st.experimental_rerun()

    def setup_styles(self):
        """스타일 설정"""
        st.markdown("""
        <style>
        .chat-message {
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .user-message {
            background-color: #e6f3ff;
        }
        .assistant-message {
            background-color: #f0f0f0;
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
            
            if "choices" in result and result["choices"]:
                return result["choices"][0]["text"].strip()
            return "응답을 생성할 수 없습니다."
            
        except Exception as e:
            st.error(f"API 호출 오류: {str(e)}")
            return "오류가 발생했습니다."

    def add_message(self, role, content):
        """메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": role,
            "content": content,
            "time": timestamp
        })

    def display_chat_history(self):
        """채팅 기록 표시"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(f"""
                <div class='chat-message {message["role"]}-message'>
                    {message["content"]}
                    <div style='font-size: 0.8em; color: gray;'>{message["time"]}</div>
                </div>
                """, unsafe_allow_html=True)

    def run(self):
        """메인 애플리케이션 실행"""
        st.title("AI 챗봇")
        
        # 채팅 기록 표시
        self.display_chat_history()
        
        # 사용자 입력 처리
        if user_input := st.chat_input("메시지를 입력하세요..."):
            # 사용자 메시지 추가
            self.add_message("user", user_input)
            
            # AI 응답 생성
            with st.spinner("AI가 응답을 생성중입니다..."):
                ai_response = self.call_llm_api(user_input)
                self.add_message("assistant", ai_response)
            
            # 화면 갱신
            st.experimental_rerun()

def main():
    app = ChatApp()
    app.run()

if __name__ == "__main__":
    main()
