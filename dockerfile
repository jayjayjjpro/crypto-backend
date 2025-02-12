# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy the requirements file first to take advantage of Docker's caching mechanism
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Command to run the application in development mode
CMD ["fastapi", "dev", "main.py"]
