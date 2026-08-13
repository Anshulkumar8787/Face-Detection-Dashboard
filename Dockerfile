# A Dockerfile is just a recipe: "start from this base, then run these
# steps to set up my app." Hugging Face Spaces reads this file and
# builds a container from it automatically.

# Start from a small, official Python 3.11 image.
FROM python:3.11-slim

# Some Python image-processing libraries (like OpenCV) need a couple
# of system-level libraries to work correctly inside a minimal
# container. This installs just those, then cleans up to keep the
# image small.
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# All commands from here on happen inside /app inside the container.
WORKDIR /app

# Copy just requirements.txt first (not the whole project yet).
# This is a Docker best practice: if only your code changes later
# (not your dependencies), Docker can reuse the already-installed
# packages instead of reinstalling everything from scratch.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project into the container.
COPY . .

# Hugging Face Spaces expects your app to listen on port 7860 —
# this line just documents that (it doesn't open the port by itself).
EXPOSE 7860

# Hugging Face Spaces containers run as a non-root user by default.
# This makes sure our upload/history/report folders are writable by
# that user, since the app needs to save files into them.
RUN mkdir -p uploads history reports && chmod -R 777 uploads history reports

# The actual command that starts the app when the container runs.
# Same gunicorn command as on Render, just bound to port 7860 instead.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
