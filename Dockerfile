# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8.5-slim-buster

# Environment variables for the configuration
ENV FLASK_APP gooutsafe.py
ENV FLASK_CONFIG docker
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Create non-root user and home folder
RUN useradd -m gooutsafe
WORKDIR /home/gooutsafe

# Install dependencies
COPY requirements/ requirements/
RUN python -m venv venv
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN venv/bin/pip install -r requirements/docker.txt 

# Move code
COPY migrations/ migrations/
COPY monolith/ monolith/
COPY gooutsafe.py config.py boot.sh ./

# Permissions
RUN chown -R gooutsafe:gooutsafe ./
RUN chmod a+x boot.sh

EXPOSE 5000
USER gooutsafe
ENTRYPOINT [ "./boot.sh" ]