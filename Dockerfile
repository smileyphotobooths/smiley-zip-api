# Use the official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy everything to the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Expose port (same as what Fly will map)
EXPOSE 8080

# Start the Flask app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
