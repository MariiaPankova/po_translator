FROM python:3.10-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY src .

# Expose the port that the application listens on.
EXPOSE 7860

# Run the application.
ENTRYPOINT python3 ui.py