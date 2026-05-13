FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码（config.json 通过环境变量或挂载覆盖，不打进镜像）
COPY src/ src/
COPY main.py .

# data 目录用于持久化（Sealos 挂载 PVC 到此路径）
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
