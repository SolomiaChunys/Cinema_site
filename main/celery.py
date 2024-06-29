import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'delete-expired-seats-every-day': {
        'task': 'cinema.tasks.delete_expired_seats',
        # 'schedule': 15.0,
        'schedule': crontab(hour='22', minute='17'),
    },
}
