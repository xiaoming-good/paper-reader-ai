# 使用官方Python基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（PDF处理需要）
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads /app/output

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 默认启动Web界面
CMD ["python", "web_app.py"]
