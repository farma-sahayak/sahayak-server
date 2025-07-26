# gateway/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set the environment variable inside the container
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

# Default command can be overridden in docker-compose
CMD ["uvicorn", "main:app", "--host", "${HOST}", "--port", "${PORT}", "--reload"]
