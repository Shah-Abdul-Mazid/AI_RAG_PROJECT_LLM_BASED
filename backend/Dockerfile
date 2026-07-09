FROM python:3.11-slim

WORKDIR /app

# Install system-level dependencies for native Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libgomp1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Command to run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
