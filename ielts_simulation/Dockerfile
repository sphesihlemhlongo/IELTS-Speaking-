# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for PortAudio
RUN apt-get update && apt-get install -y \
    alsa-utils \
    pulseaudio \
    jackd2 \
    libasound2-dev \
    libjack-jackd2-dev \
    portaudio19-dev \
    libsndfile1 \
    sox\
    && apt-get clean

# Set environment variables for audio
ENV PULSE_SERVER=host.docker.internal


# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service account key file (update the filename)
COPY service-account-key.json /app/service-account-key.json

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run the Flask app when the container launches
CMD ["python", "app.py"]
