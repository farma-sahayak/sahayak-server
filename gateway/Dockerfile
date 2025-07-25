# gateway/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Default command can be overridden in docker-compose
CMD ["uvicorn", "main:app", "--host", "${HOST}", "--port", "${PORT}", "--reload"]
