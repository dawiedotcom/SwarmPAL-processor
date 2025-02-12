# Setup with uv
# https://docs.astral.sh/uv/guides/integration/docker/
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.5.30 /uv /uvx /bin/
ENV UV_NO_CACHE=1
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Install Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies and activate environment
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"

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
