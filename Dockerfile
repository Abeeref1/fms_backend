# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY src /app/src
COPY migrations /app/migrations

# Expose default Render port
EXPOSE 10000

# Run via Gunicorn/Uvicorn
CMD ["gunicorn", "src.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000"]

