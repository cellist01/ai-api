FROM python:3.9-slim

WORKDIR /app

# 필요한 패키지만 설치
RUN pip install streamlit==1.28.0 requests==2.31.0

# 앱 코드 복사
COPY app.py .

# OpenShift 권한 설정
RUN chgrp -R 0 /app && \
    chmod -R g=u /app

USER 1001

ENV PORT=8501
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

EXPOSE 8501

# streamlit 명령어를 직접적으로 실행
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress=0.0.0.0 \
    --server.enableCORS=false \
    --client.showErrorDetails=true
