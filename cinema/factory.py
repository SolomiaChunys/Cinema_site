from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from datetime import date, timedelta
import factory
from .models import (
    AvailableSeats,
    CinemaHall,
    Session,
    Ticket,
    Film,
)

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = 'Rose'
    email = 'rose@gmail.com'

    is_active = True
    is_superuser = False
    is_staff = False


class AdminFactory(UserFactory):
    class Meta:
        model = User

    username = 'admin'
    email = 'admin@gmail.com'
    password = 'admin1234_'

    is_staff = True
    is_superuser = True


class HallFactory(DjangoModelFactory):
    class Meta:
        model = CinemaHall

    name = 'Hall№9'
    size = 10


class FilmFactory(DjangoModelFactory):
    class Meta:
        model = Film

    name = 'Batman'
    genre = 'fantasy'
    image = 'images/anime1.jpg'


class SessionFactory(DjangoModelFactory):
    class Meta:
        model = Session

    film = factory.SubFactory(FilmFactory)
    hall = factory.SubFactory(HallFactory)
    price = '79.01'
    start_time = '10:00'
    end_time = '12:00'
    start_date = factory.LazyAttribute(lambda _: date.today())
    end_date = factory.LazyAttribute(lambda _: date.today() + timedelta(days=5))


class TicketFactory(DjangoModelFactory):
    class Meta:
        model = Ticket

    user = factory.SubFactory(UserFactory)
    session = factory.SubFactory(SessionFactory)
    count_of_tickets = '1'
    total_price = '79.00'
    data_session = factory.LazyAttribute(lambda _: date.today() + timedelta(days=1))


class AvailableSeatsFactory(DjangoModelFactory):
    class Meta:
        model = AvailableSeats

    session = factory.SubFactory(SessionFactory)
    date = factory.LazyAttribute(lambda _: date.today())
    occupied_seats = 10
