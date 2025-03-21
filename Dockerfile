FROM python:3.9

# Set up the app directory for dependencies
WORKDIR /

# Copy dependency files
COPY pyproject.toml pdm.lock* ./

# Install dependencies
RUN pip install pdm
RUN pdm install --prod

# Keep the app directory as the working directory
# This ensures pdm can find the pyproject.toml file
WORKDIR /src
CMD pdm run uvicorn serve:app --host 0.0.0.0 --port ${APP_PORT} --reload