FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies (cached layer for speed)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project code
COPY . .

# Expose application port
EXPOSE 8000

# Run Django using Gunicorn (WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ApplicationService.wsgi:application"]
