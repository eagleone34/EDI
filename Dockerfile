FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Use Python script that properly reads PORT env variable
CMD ["python", "start.py"]
