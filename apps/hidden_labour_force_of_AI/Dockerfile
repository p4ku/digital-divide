FROM python:3.11.5-slim
ARG APP_PATH
ARG REQUIREMENTS_PATH
ARG CONFIG_PATH

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY ${REQUIREMENTS_PATH} .
COPY ${CONFIG_PATH} /root/.streamlit/config.toml
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.baseUrlPath=${BASE_URL_PATH}
