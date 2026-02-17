# Dockerfile for bt-sec-analyzer
# Uses Arch Linux base for compatibility with target platform

FROM archlinux:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    python \
    python-pip \
    bluez \
    bluez-utils \
    git \
    curl \
    base-devel \
    && pacman -Scc --noconfirm

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Create app directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Install Python dependencies
RUN poetry install --no-root --no-dev

# Copy application code
COPY . /app/

# Install the application
RUN poetry install --no-dev

# Create necessary directories
RUN mkdir -p /app/logs /app/reports /app/sessions /app/captures

# Expose any necessary ports (if needed for web UI)
# EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["poetry", "run", "python", "-m", "bt_sectester"]

# Default command (can be overridden)
CMD ["--help"]
