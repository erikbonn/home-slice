# Use an official Python image as the base
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set environment variables (optional, can also be set in Railway dashboard)
# ENV DB_HOST=...
# ENV DB_PORT=5432
# ENV DB_NAME=...
# ENV DB_USER=...
# ENV DB_PASSWORD=...
# ENV FRED_API_KEY=...

# Command to run the application
CMD ["python3", "fetch_redfin.py"]