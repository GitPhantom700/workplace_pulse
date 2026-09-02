# Use official Python 3.11 slim image for minimal footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Cloud Run default port
EXPOSE 8080

# Command to run the FastAPI application using Uvicorn with dynamic Cloud Run $PORT support
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
