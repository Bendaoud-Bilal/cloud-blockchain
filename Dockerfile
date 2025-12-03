# Dockerfile for Blockchain Node
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy blockchain node files
COPY blockchain/ ./blockchain/

# Create data directory for persistence
RUN mkdir -p /app/data

WORKDIR /app/blockchain

# Expose default port
EXPOSE 5000

# Run the blockchain node - bind to 0.0.0.0 for Docker networking
CMD ["python", "blockchain.py", "-p", "5000"]
