# Use the official Python image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install Poetry and the project dependencies
RUN pip install poetry && poetry install --no-dev

# Expose the default port for the server
EXPOSE 8080

# Start the MimickerServer using poetry and Python
CMD ["poetry", "run", "python", "-c", "from mimicker.server import MimickerServer; MimickerServer().start()"]
