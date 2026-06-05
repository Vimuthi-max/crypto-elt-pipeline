# 1. Base Image Setup
FROM python:3.10-slim

# 2. Setup Working Directory
WORKDIR /app

# 3. Cache and Install Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Application Source Code
COPY . .

# 5. Pipeline Entry Point
CMD ["python", "pipeline.py"]