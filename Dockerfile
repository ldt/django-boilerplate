FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy pyproject.toml and uv.lock
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-dev

# Copy project
COPY . .

# Collect static files
RUN uv run manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]