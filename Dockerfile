# Use the official Python image as a base image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Copy the entire current directory's contents into the container's /app directory
COPY . .

# Install required dependencies
RUN pip install -r requirements-dev.txt

# Set the PYTHONPATH environment variable to include the project root directory
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Define the command to be run when the container starts
ENTRYPOINT ["python", "src/cli.py"]
