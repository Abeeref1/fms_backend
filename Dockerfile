# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for some Python packages if needed
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY src /app/src
COPY migrations /app/migrations
# Note: The SQLite DB file will be created by migrations inside the container

# Expose the port the app runs on (Render default is 10000)
EXPOSE 10000

# Define the command to run the application
# Gunicorn will bind to 0.0.0.0:10000 by default when PORT env var is set by Render
# Ensure create_app() is callable
CMD ["gunicorn", "src.main:create_app()", "--bind", "0.0.0.0:10000"]
