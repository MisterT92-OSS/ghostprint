FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install GhostPrint
RUN pip install -e .

# Create directory for results
RUN mkdir -p /app/results

# Set entrypoint
ENTRYPOINT ["ghostprint"]
CMD ["--help"]