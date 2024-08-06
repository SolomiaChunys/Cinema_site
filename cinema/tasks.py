from celery import shared_task
from django.utils import timezone
from cinema.models import AvailableSeats, Session


@shared_task
def delete_expired_seats():
    today = timezone.now().date()
    expired_seats = AvailableSeats.objects.filter(date__lt=today)
    expired_sessions = Session.objects.filter(end_date__lt=today)
    expired_seats.delete()
    expired_sessions.delete()
    return f'Successfully deleted expired AvailableSeats, Sessions records'


# celery -A main worker -l INFO
# celery -A main worker -l INFO --pool=solo (запустити завдання)
# celery -A main beat -l INFO

