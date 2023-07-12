FROM python:3.11.4

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

ARG API_UID

RUN apt-get update && \
    apt-get install --yes --no-install-recommends vim

# Clean up after building.
RUN  apt-get autoremove && apt-get clean && rm -rf /var/lib/apt/lists/*

# User setup
RUN useradd -u $API_UID -g 0 dirac

RUN mkdir -p /app/api && \
    chown -R $API_UID:0 /app

WORKDIR /app
USER dirac

# Install as a non-root user
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Update pip
RUN pip install --no-cache-dir -U pip

# Copy source directories and install
COPY --chown=dirac:root ./api/pyproject.toml /app/api

RUN pip install --no-cache-dir /app/api

COPY --chown=dirac:root ./api/src/api /app/api

# Run the app
ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
