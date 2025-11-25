FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    graphviz \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install production WSGI server
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create screenshots directory
RUN mkdir -p screenshots

# Expose port
EXPOSE 5000

# Run database initialization and start server
CMD ["sh", "-c", "python create_db.py && gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app"]
