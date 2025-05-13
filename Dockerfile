# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-alpine

EXPOSE 8000
ENV YOUR_ENV="production" \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 

# Keeps Python from generating .pyc files in the container
# ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

#System deps:
RUN apk add --no-cache firefox

# Copy only requirements to cache them in docker layer

WORKDIR /app
RUN adduser --disabled-password --gecos "FusionPBX API" fpbxapi


COPY --chown=fpbxapi . /app/

# Project initialization:
RUN pip install -r requirements.txt
# RUN alembic upgrade head

# Creating folders, and files for a project:
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers

USER fpbxapi

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["uvicorn", "--ssl-keyfile=${SSL_PRIVATE_KEY}", "--ssl-certfile=${SSL_CERTIFICATE}", "--host=0.0.0.0", "--port=8000", "fusionpbx_pilot_api.services.restapi:app"]
CMD [ "./run.sh" ]
