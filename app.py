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
