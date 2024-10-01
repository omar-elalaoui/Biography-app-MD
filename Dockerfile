# Use the official Python image from the Docker Hub
FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP run.py

# Create a directory for the application
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port that the application will run on
EXPOSE 5000

# Define the command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]