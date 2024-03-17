FROM python:3.12-slim
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

ADD app.ipynb /app
ADD start-dashboard.sh /app
RUN chmod +x /app/start-dashboard.sh
