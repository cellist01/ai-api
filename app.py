import streamlit as st
import requests
from datetime import datetime

# 세션 상태 초기화를 가장 먼저, 다른 st 명령어보다 앞에 배치
if "messages" not in st.session_state:
    st.session_state["messages"] = []    # 대괄호 표기법 사용

def main():
    st.title("AI 챗봇")

    # 채팅 이력 표시
    for msg in st.session_state["messages"]:    # 대괄호 표기법 사용
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 사용자 입력 처리
    if user_input := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state["messages"].append({    # 대괄호 표기법 사용
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%H:%M")
        })

        # AI 응답 생성
        with st.spinner("응답 생성 중..."):
            ai_response = call_llm_api(user_input)
            st.session_state["messages"].append({    # 대괄호 표기법 사용
                "role": "assistant",
                "content": ai_response,
                "time": datetime.now().strftime("%H:%M")
            })
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
