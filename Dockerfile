FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD python manage.py migrate \
    && python manage.py makemigrations \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')"  \
    && python manage.py collectstatic --noinput \
    && gunicorn main.wsgi:application --bind 0.0.0.0:8000