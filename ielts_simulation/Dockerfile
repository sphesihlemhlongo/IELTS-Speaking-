# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
# COPY ./pulseaudio-1.1 /app/

# Install system dependencies for PortAudio
# RUN apt-get update --fix-missing? && apt-get install -y \
#     alsa-utils \
#     jackd2 \
#     libasound2 \
#     libasound2-dev \
#     libjack-jackd2-dev \
#     portaudio19-dev \
#     libsndfile1 \
#     sox\
#     build-essential \
#     ffmpeg \
#     && apt-get clean

RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    libasound2-dev \
    pulseaudio\
    alsa-utils\
    libjack-jackd2-dev \
    && apt-get clean

RUN getent group audio || groupadd -r audio
RUN usermod -aG audio app_user || true

# Set environment variables for audio
# ENV PULSE_SERVER=host.docker.internal
# ENV PULSE_SERVER=unix:/tmp/pulse-native

# RUN mkdir -p /tmp/pulse

# COPY requirements.txt .


# Install any needed packages specified in requirements.txt
# RUN pip install --upgrade pip
RUN pip install --default-timeout=100 -r requirements.txt


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
