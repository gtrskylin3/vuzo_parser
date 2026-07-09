FROM python:3.11-slim

# Set environment variables to optimize Python inside Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set the working directory inside the container
WORKDIR /app

# Copy only dependency definitions first to leverage Docker caching
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

# Install dependencies without saving local pip cache
RUN uv sync --frozen --no-cache

# Copy the rest of the application files
COPY . .

CMD ["uv", "run", "main.py"]