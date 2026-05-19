FROM python:3.11-slim
WORKDIR /app

# Copy requirements from the root context
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the contents of the api directory into /app
COPY api/ .

# Ensure data directory exists
RUN mkdir -p /app/data

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]