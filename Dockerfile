# Use Python 3.10 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Add build argument for script name
ARG AGENT_SCRIPT_NAME
ENV AGENT_SCRIPT_NAME=${AGENT_SCRIPT_NAME:-main.py}

# Install dependencies first, for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV RUN_AS_API=1

# Copy project files
COPY . .

RUN useradd -m ossboss && mkdir -p /app/tmp && chown ossboss:ossboss /app/tmp
USER ossboss

# Set environment variables (these will need to be overridden at runtime)
ENV GITHUB_TOKEN="" \
    MONGO_DB_URL="mongodb://mongodb:27017/ossboss" \
    API_HOST="0.0.0.0" \
    API_PORT="8000" \
    TELEGRAM_BOT_TOKEN="" \
    DO_DEPLOYMENT=false

# Expose API port
EXPOSE 8000

# Default command (run all interfaces)
# This can be overridden with docker run command
CMD ["sh", "-c", "python ${AGENT_SCRIPT_NAME}"]