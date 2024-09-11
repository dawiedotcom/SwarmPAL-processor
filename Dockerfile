FROM python:3.12-slim
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add dashboards
WORKDIR /app
RUN mkdir /app/dashboards
ADD dashboards/fac-fast.py /app/dashboards
# Add processors
RUN mkdir /app/tasks
ADD tasks/fac-fast-processor.py /app/tasks
ADD tasks/start_tasks.sh /app/tasks

# Copy the entrypoint script and set it
# NB: container must be supplied with $VIRES_TOKEN at runtime (e.g. via .env file)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
