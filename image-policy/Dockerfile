# Use an official lightweight Python image
FROM python:3.9-slim

#install required packages
RUN pip install flask gunicorn

# Set the working directory inside the container
WORKDIR /app

# Copy the application files
COPY mutating_webhook_imagepolicy.py .  
COPY server.crt server.key .  

# Install dependencies
RUN pip install flask

# Expose the port that the webhook server listens on
EXPOSE 443

# Run the Flask app
CMD ["gunicorn", "--certfile=server.crt", "--keyfile=server.key", "-b", "0.0.0.0:443", "mutating_webhook:app"]