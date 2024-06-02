FROM python:3.10-slim

WORKDIR /bot

# Set the environment variable for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    python3-pip \
    build-essential && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Read the .env file and set environment variables as build-time arguments
ARG BOT_TOKEN
ARG ADMIN_IDS
ARG API_KEY
ARG HOST
ARG PORT
ARG DB_USER
ARG PASSWORD
ARG DATABASE

# Set environment variables based on build-time arguments
ENV BOT_TOKEN=$BOT_TOKEN
ENV ADMIN_IDS=$ADMIN_IDS
ENV API_KEY=$API_KEY
ENV HOST=$HOST
ENV PORT=$PORT
ENV DB_USER=$DB_USER
ENV PASSWORD=$PASSWORD
ENV DATABASE=$DATABASE

COPY requirements.txt /bot/
RUN pip install -r /bot/requirements.txt

COPY ./bot ./bot

# Set the entrypoint to run the bot
ENTRYPOINT ["python3", "-m", "bot.main"]