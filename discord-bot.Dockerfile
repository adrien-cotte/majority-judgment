# Use the official Python image as the base image
FROM python

# Define build-time variables for the bot token and guild IDs
ARG MAJOR_BOT_TOKEN
ARG MAJOR_BOT_GUILDS

# Update the package list
RUN apt update

# Install cmake, which may be required for building some Python packages
RUN apt install -y cmake

# Install Python dependencies using pip
RUN pip install matplotlib pandas disnake

# Copy the current directory (where the Dockerfile is located) into the image at /majority-judgement
COPY . /majority-judgement

# Set environment variables inside the container using the values from build arguments
ENV MAJOR_BOT_TOKEN=${MAJOR_BOT_TOKEN}
ENV MAJOR_BOT_GUILDS=${MAJOR_BOT_GUILDS}

# Set the working directory to where your bot's main script is located
WORKDIR /majority-judgement/discord-bot

# Define the command to run your bot when the container starts
CMD ["/usr/local/bin/python3", "major_bot.py"]
