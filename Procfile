web: cd backend && python manage.py migrate --noinput && python manage.py seed_data 2>/dev/null; gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
