import streamlit as st
import requests
from datetime import datetime

def init_session_state():
    # 세션 상태 명시적 초기화
    if not hasattr(st.session_state, 'messages'):
        st.session_state.messages = []

def main():
    st.title("AI 챗봇")

    # 초기화 호출
    init_session_state()

    # 채팅 이력 표시
    if hasattr(st.session_state, 'messages'):
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 저장
        st.session_state.messages.append({"role": "user", "content": prompt})

        # AI 응답 생성
        response = call_llm_api(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

def call_llm_api(prompt):
    """LLM API 호출"""
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
        return response.json()["choices"][0]["text"]
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    main()
