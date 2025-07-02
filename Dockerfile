# ---- Stage 1: The Builder ----
# This stage installs all dependencies (including dev) and runs tests.
FROM python:3.9-slim as builder

WORKDIR /app

# Use --no-cache-dir to prevent caching issues
RUN pip install --no-cache-dir poetry

# Copy only the dependency files first to leverage Docker's layer cache efficiently.
COPY pyproject.toml poetry.lock* ./

# Install ALL dependencies, including dev dependencies like pytest, for testing.
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction

# Copy the rest of the application code into the container
COPY . .

# Run the unit tests. If this command fails, the 'docker build' will stop,
# failing the CI pipeline stage correctly.
RUN poetry run pytest


# ---- Stage 2: The Final Production Image ----
# This stage creates the small, final image that will be deployed.
FROM python:3.9-slim

WORKDIR /app

# Install poetry again, it's a small build tool.
RUN pip install --no-cache-dir poetry

# Copy only the dependency files from the host
COPY pyproject.toml poetry.lock* ./

# Install ONLY production dependencies. This makes the final image smaller
# and more secure by excluding tools like pytest.
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root --no-interaction

# Copy the validated application code from the 'builder' stage.
# We copy from the builder because we know its tests have passed.
COPY --from=builder /app .

# Expose the port the app runs on
EXPOSE 8000

# The command to run the application using a production-ready server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
