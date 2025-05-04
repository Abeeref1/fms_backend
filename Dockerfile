# Use official slim Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port Render uses
EXPOSE 10000

# Launch via Gunicorn + Uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:10000"]
