# 使用官方的Python运行时作为父镜像
FROM python:3.11.2

# 将工作目录设置为/app
WORKDIR /app

# 将当前目录的内容添加到容器的/app目录中
ADD . /app

# 安装在requirements.txt中指定的任何所需包
RUN pip install --no-cache-dir -r requirements.txt