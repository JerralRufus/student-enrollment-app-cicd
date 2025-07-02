# Start with an official Python runtime as a parent image
FROM python:3.9-slim
# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only the files needed for dependency installation to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install dependencies without creating a virtual environment inside the container
# and without the dev dependencies
RUN poetry config virtualenvs.create false && poetry install --without dev --no-root

# Copy the rest of the application code into the container
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run the application
# We use Gunicorn, a production-ready WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
