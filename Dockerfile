# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install system dependencies for MySQL client
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    python3-dev \
    libssl-dev \
    libffi-dev \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt before installing dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose port 8080 for cloud
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=server.py

# Run the Flask application
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
