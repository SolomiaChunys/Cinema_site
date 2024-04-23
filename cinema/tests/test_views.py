from datetime import date, timedelta
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from cinema.factory import (
    UserFactory,
    SessionFactory,
    AdminFactory,
    HallFactory,
    FilmFactory,
    TicketFactory,
)
from cinema.models import Ticket, CinemaHall

User = get_user_model()


class SessionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.session = SessionFactory()
        self.admin = AdminFactory()
        self.hall = HallFactory()
        self.film = FilmFactory()

    def test_list_session(self):
        url = reverse('schedule_page')
        response = self.client.get(url)
        context = response.context
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cinema/schedule.html')

        session_tomorrow = SessionFactory(start_date=date.today() + timedelta(days=1))

        # Test data-filter today
        self.assertNotIn(session_tomorrow, context['object_list'])
        self.assertEqual(str(context['date_filter']), 'today')
        self.assertEqual(str(context['time_filter']), 'end_time')

        response = self.client.get(url, {'date-filter': 'tomorrow'})
        context = response.context

        # Test data-filter tomorrow
        self.assertEqual(response.status_code, 200)
        self.assertIn(session_tomorrow, context['object_list'])
        self.assertEqual(str(context['date_filter']), 'tomorrow')

    def test_list_session_message(self):
        # Test with sold message
        url = reverse('schedule_page')
        response = self.client.get(url, {'sold_message': 'True'})
        context = response.context
        messages = [m.message for m in context['messages']]
        self.assertIn('All tickets for this session have already been sold!', messages)

    def test_create_session(self):
        url = reverse('create_session')
        data = {
            'film': self.film.pk,
            'hall': self.hall.pk,
            'price': '100.00',
            'start_time': '10:00',
            'end_time': '12:00',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=5)
        }

        # Admin Access
        self.client.force_login(self.admin)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('create_session'))

        # User Access
        self.client.force_login(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_update_session(self):
        url = reverse('update_session', args=[self.session.pk])
        new_data = {
            'film': self.film.pk,
            'hall': self.hall.pk,
            'price': self.session.price,
            'start_time': self.session.start_time,
            'end_time': self.session.end_time,
            'start_date': date.today(),
            'end_date': self.session.end_date,
        }

        response = self.client.put(url, new_data)
        self.assertEqual(response.status_code, 302)


class HallTestCase(TestCase):
    def setUp(self):
        self.hall = HallFactory()
        self.admin = AdminFactory()
        self.client = Client()
        self.client.force_login(self.admin)

    def test_create_hall(self):
        url = reverse('create_hall')
        data = {
            'name': 'Hall10',
            'size': '5',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_update_hall(self):
        url = reverse('update_hall', args=[self.hall.pk])
        new_data = {
            'name': 'Hall№9',
            'size': '15',
        }
        # Test Valid update
        response = self.client.post(url, new_data, HTTP_X_HTTP_METHOD_OVERRIDE='PUT')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CinemaHall.objects.get(id=self.hall.id).size, int(new_data['size']))

    def test_update_hall_invalid(self):
        # Test Invalid update
        new_data = {
            'name': 'Hall№9',
            'size': '15',
        }
        url = reverse('update_hall', args=[self.hall.pk])
        TicketFactory(session__hall=self.hall)
        response = self.client.post(url, new_data, HTTP_X_HTTP_METHOD_OVERRIDE='PUT')
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(CinemaHall.objects.get(id=self.hall.id).size, int(new_data['size']))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Tickets have already been booked in this hall!")


class TicketTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.session = SessionFactory()
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_valid_create_ticket(self):
        # Test Valid booking
        url = reverse('book_ticket',  kwargs={'pk': self.session.pk, 'date_filter': 'tomorrow'})
        data = {
            'count_of_tickets': 3,
        }
        response_valid = self.client.post(url, data)
        self.assertRedirects(response_valid, reverse('schedule_page'))
        self.assertEqual(Ticket.objects.filter(user=self.user).count(), 1)

    def test_invalid_count_of_ticket(self):
        # Test Invalid count of tickets
        url = reverse('book_ticket', kwargs={'pk': self.session.pk, 'date_filter': 'tomorrow'})
        data = {
            'count_of_tickets': 0,
        }
        response_invalid = self.client.post(url, data)
        self.assertRedirects(response_invalid, reverse('schedule_page'))

        messages = list(get_messages(response_invalid.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Count of tickets must be greater than zero!")

    def test_invalid_available_seats(self):
        # Test available seats
        url = reverse('book_ticket', kwargs={'pk': self.session.pk, 'date_filter': 'tomorrow'})
        available_seats = self.session.available_tomorrow()
        count_of_tickets = available_seats + 1

        data = {
            'count_of_tickets': count_of_tickets,
        }
        response_invalid_seats = self.client.post(url, data)
        self.assertRedirects(response_invalid_seats, reverse('schedule_page'))

        messages = list(get_messages(response_invalid_seats.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Not enough available seats!")

    def test_ticket_list(self):
        TicketFactory(user=self.user, session=self.session)
        url = reverse('booked_tickets')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cinema/booked_tickets.html')
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertEqual(response.context['object_list'][0].user, self.user)
