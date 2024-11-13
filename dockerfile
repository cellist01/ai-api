FROM python:3.9-slim

WORKDIR /app

# 필요한 패키지 설치
RUN pip install streamlit==1.28.0 requests==2.31.0

# 앱 코드 복사
COPY app.py .

# OpenShift 권한 설정
RUN chgrp -R 0 /app && \
    chmod -R g=u /app

USER 1001

# 환경 변수 설정
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

EXPOSE 8501

# python -m streamlit 형식으로 실행
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
