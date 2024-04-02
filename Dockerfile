ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim as base

# Copy the requirements file into the container.
COPY requirements.txt .

# Install the dependencies from the requirements file.
RUN python -m pip install --no-cache-dir -r requirements.txt

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app
# Copy the source code into the container.
COPY . .

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
# Switch to the non-privileged user to run the application.
USER 1001

# set entrypoint for interactive shells
ENTRYPOINT [ "rasa" ]

# Expose the port that the application listens on.
EXPOSE 7860

# List of Models: central+careersv1.0.tar.gz,Arpit-v1.0.tar.gz,Maisam+Arpit+Anand+Pankaj-bot-v1.0.tar.gz

# Run the application.
CMD ["run","--model","models/20240308-051705-convex-tonic.tar.gz","--enable-api","--port","7860"]