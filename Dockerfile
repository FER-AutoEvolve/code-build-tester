# Base stage: always builds the main app
FROM python:3.12-slim AS base

WORKDIR /app

COPY ./src /app
COPY ./requirements.txt /app/requirements.txt
COPY ./configuration.template.json /app/configuration.template.json

RUN pip install --upgrade pip && \
    pip install -r ./requirements.txt

RUN apt-get update
RUN apt-get install -y curl ca-certificates gnupg
# Add NodeSource repository for Node.js 22.x
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
# Install Node.js (comes with npm)
RUN apt-get install -y nodejs

RUN apt-get install -y gettext-base


# Set arguments for environment variables (one per line)
ARG CODE_DIRECTORY="./codebase"
ARG CODE_STAGING_DIRECTORY="./codebase_staging"
ARG CODE_BUILD_DIRECTORY="./codebase_build"
ARG CODE_BUILDER_TYPE="NPM_VITE"
ARG FASTAPI_HOST="0.0.0.0"
ARG FASTAPI_PORT=2000
ARG KEYPOINT_NOTIFICATION_ENABLED="false"
ARG KEYPOINT_NOTIFICATION_ENDPOINT="http://game-web-wrapper:8001/notify-of-event"
ARG EXPERIMENT_NOTIFICATION_ENABLED="true"
ARG EXPERIMENT_NOTIFICATION_ENDPOINT="http://experiment-director:8002/notify"
ARG EXPERIMENT_NOTIFICATION_COMPONENT_NAME="CODE_BUILD_TESTER"


# Set default environment variables
ENV CODE_DIRECTORY=${CODE_DIRECTORY} \
    CODE_STAGING_DIRECTORY=${CODE_STAGING_DIRECTORY} \
    CODE_BUILD_DIRECTORY=${CODE_BUILD_DIRECTORY} \
    CODE_BUILDER_TYPE=${CODE_BUILDER_TYPE} \
    FASTAPI_HOST=${FASTAPI_HOST} \
    FASTAPI_PORT=${FASTAPI_PORT} \
    KEYPOINT_NOTIFICATION_ENABLED=${KEYPOINT_NOTIFICATION_ENABLED} \
    KEYPOINT_NOTIFICATION_ENDPOINT=${KEYPOINT_NOTIFICATION_ENDPOINT} \
    EXPERIMENT_NOTIFICATION_ENABLED=${EXPERIMENT_NOTIFICATION_ENABLED} \
    EXPERIMENT_NOTIFICATION_ENDPOINT=${EXPERIMENT_NOTIFICATION_ENDPOINT} \
    EXPERIMENT_NOTIFICATION_COMPONENT_NAME=${EXPERIMENT_NOTIFICATION_COMPONENT_NAME}

RUN envsubst < /app/configuration.template.json > /app/configuration.json
RUN rm /app/configuration.template.json

EXPOSE ${FASTAPI_PORT}

CMD ["python", "/app/main.py", "--config", "/app/configuration.json"]

# with_codebase stage: includes codebase directory
FROM base AS with_codebase

COPY ./codebase /app/codebase
COPY ./codebase_staging /app/codebase_staging
