# 可通过 build-arg 换成国内镜像，例如：
#   docker compose build --build-arg BASE_IMAGE=docker.m.daocloud.io/library/python:3.12-slim
ARG BASE_IMAGE=python:3.12-slim
FROM ${BASE_IMAGE}

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120

COPY requirements.txt .

# 使用阿里云 PyPI，超时/重试加大，避免卡在 Downloading
RUN pip install --no-cache-dir \
    --retries 10 \
    --timeout 120 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt

COPY . .

EXPOSE 5674

CMD gunicorn -b 0.0.0.0:${APP_PORT:-5674} -w 2 --timeout 120 visualAnalysis:app
