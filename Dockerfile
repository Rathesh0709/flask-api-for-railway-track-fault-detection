FROM python:3.11-slim

# System dependencies required by OpenCV and YOLO
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender-dev \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Set port for Google Cloud Run
ENV PORT=8080
EXPOSE 8080

# Run the app
CMD ["python", "test.py"]
