FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create outputs directory
RUN mkdir -p outputs

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV HOST=0.0.0.0

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "${HOST}:${PORT}", "wsgi:app"]
