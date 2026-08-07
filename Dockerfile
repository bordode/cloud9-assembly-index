FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install python dependencies first (cached by Docker)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port the app will run on
EXPOSE 8080

# Create non-root user and set ownership
RUN useradd -U -u 1000 appuser && chown -R 1000:1000 /app
USER 1000

# Use gunicorn to serve the Flask app (matches Procfile)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080"]
