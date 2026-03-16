FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-xlib-2.0-dev \
    libffi-dev \
    libxcb1-dev \
    libxcb-render0-dev \
    libxcb-shm0-dev \
    libxcb-xfixes0-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN cd backend && python manage.py collectstatic --noinput

EXPOSE 8080
CMD cd backend && python manage.py migrate --noinput && python manage.py seed_data 2>/dev/null; gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
