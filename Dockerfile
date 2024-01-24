# Use the official Python image as the base image
FROM python:3.9-slim

# Set environment variables
ENV SERVER_PORT=8765
ENV TOKEN="your_token"
ENV HOSTS_FILE="hosts.txt"
ENV WEBPATH="/update"

# Set the working directory
WORKDIR /app

# Copy the Python script to the container
COPY hostsCallback.py /app/hostsCallback.py

# Expose the port that the server will run on
EXPOSE $SERVER_PORT

# Run the Python script when the container starts
CMD ["python", "hostsCallback.py"]
