from django.contrib.auth.models import AbstractUser
from datetime import datetime, date, timedelta
from django.db import models


class User(AbstractUser):
    total_spent = models.DecimalField(decimal_places=2, default=0, max_digits=12)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username}"


class CinemaHall(models.Model):
    name = models.CharField(max_length=100)
    size = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Film(models.Model):
    name = models.CharField(max_length=100)
    genre = models.TextField()
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name


class Session(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='session_film')
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='session_hall')
    price = models.DecimalField(decimal_places=2, max_digits=12)
    start_time = models.TimeField(default=datetime.now().strftime("%H:%M"))
    end_time = models.TimeField(default=datetime.now().strftime("%H:%M"))
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)

    def __str__(self):
        return f'{self.film.name} from {self.start_date.strftime("%d")} to {self.end_date.strftime("%d, %Y")}'

    class Meta:
        ordering = ['start_date']

    def create_available(self, date):
        available_seats_obj, created = AvailableSeats.objects.get_or_create(session=self, date=date)
        return self.hall.size - available_seats_obj.occupied_seats

    def available_today(self):
        today = date.today()
        return self.create_available(today)

    def available_tomorrow(self):
        tomorrow = date.today() + timedelta(days=1)
        return self.create_available(tomorrow)


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    count_of_tickets = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(decimal_places=2, max_digits=12)
    data_session = models.DateField(default=date.today)
    data_creation = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.session.hall.name} - {self.session.start_time.strftime("%H:%M")}'

    class Meta:
        ordering = ['-data_creation']


class AvailableSeats(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    occupied_seats = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.session} - {self.date}"

    class Meta:
        unique_together = ('session', 'date')