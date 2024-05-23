# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies for Poppler and libgl1-mesa-glx
# First update the package list and install poppler-utils and libgl1-mesa-glx
RUN apt-get update && \
    apt-get install -y --no-install-recommends poppler-utils libgl1-mesa-glx && \
    apt-get install ffmpeg libsm6 libxext6 -y && \
    apt-get install tesseract-ocr libtesseract-dev -y && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies using pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose port 5000 for the application
EXPOSE 5000

# Set the default command to run the Python file
CMD ["python", "server.py"]