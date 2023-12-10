# Dockerfile for data processing component

# Use an official Python runtime as a base image
FROM python:latest

# Set the working directory in the container to /app
WORKDIR /app

# Copy the Python script and any other necessary files
COPY data_processing/data_processing.py /app/
COPY requirements.txt /app/
COPY infofile.py /app/  
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run when starting the container
CMD ["python", "./data_processing.py"]