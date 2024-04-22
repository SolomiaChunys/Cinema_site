from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from datetime import date, timedelta
from rest_framework import status
from django.urls import reverse
from cinema.factory import (
    UserFactory,
    SessionFactory,
    AdminFactory,
    HallFactory,
    FilmFactory,
    TicketFactory,
    AvailableSeatsFactory
)

User = get_user_model()


class SessionListAPITestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.session = SessionFactory(start_date=date.today() + timedelta(days=1))
        self.session_today = SessionFactory(price=250, start_time='12:50')

    def test_get_list(self):
        url = reverse('session-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_date_filter_tomorrow(self):
        url = reverse('session-list')

        response = self.client.get(url, {'date-filter': 'tomorrow'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[1]['id'], self.session.id)

    def test_date_filter_today(self):
        url = reverse('session-list')
        response = self.client.get(url, {'date-filter': 'today'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.session_today.id)

    def test_price_filter(self):
        self.session_correct_price = SessionFactory(price=60)

        url = reverse('session-list')
        response = self.client.get(url, {'price_from': 60, 'price_to': 80, 'date-filter': 'tomorrow'})

        self.assertEqual(len(response.data), 2)
        self.assertIn(self.session_correct_price.id, [session['id'] for session in response.data])
        self.assertNotIn(self.session_today.id, [session['id'] for session in response.data])

    def test_hall_filter(self):
        self.session_correct_hall = SessionFactory(hall__id=6)

        url = reverse('session-list')
        response = self.client.get(url, {'hall_id': 6})

        self.assertEqual(len(response.data), 1)

    def test_time_filter(self):
        url = reverse('session-list')
        response = self.client.get(url, {'time_from': '12:00', 'time_to': '13:00'})

        self.assertEqual(len(response.data), 1)


class SessionAPITestCase(APITestCase):
    def setUp(self):
        self.admin = AdminFactory()
        self.client.force_authenticate(user=self.admin)
        self.session_data = {
            'film': FilmFactory().pk,
            'hall': HallFactory().pk,
            'price': '100.00',
            'start_time': '10:00',
            'end_time': '12:00',
            'start_date': '2024-04-25',
            'end_date': '2024-04-30'
        }

    def test_create_session(self):
        url = reverse('session-create')
        response = self.client.post(url, self.session_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_session(self):
        session = SessionFactory()

        url = reverse('session-update', kwargs={'pk': session.pk})
        response = self.client.put(url, self.session_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_session(self):
        session = SessionFactory()
        TicketFactory(session=session)

        url = reverse('session-update', kwargs={'pk': session.pk})
        response = self.client.put(url, self.session_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Tickets have already been booked for this session!', response.data)


class HallAPITestCase(APITestCase):
    def setUp(self):
        self.admin = AdminFactory()
        self.client.force_authenticate(user=self.admin)
        self.hall_data = {
            'name': 'Hall10',
            'size': '5',
        }

    def test_create_hall(self):
        url = reverse('hall-create')
        response = self.client.post(url, self.hall_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_hall(self):
        hall = HallFactory()

        url = reverse('hall-update', kwargs={'pk': hall.pk})
        response = self.client.put(url, self.hall_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_hall(self):
        hall = HallFactory()
        TicketFactory(session__hall=hall)

        url = reverse('hall-update', kwargs={'pk': hall.pk})
        response = self.client.put(url, self.hall_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Tickets have already been booked in this hall!', response.data)


class TicketAPITestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.session = SessionFactory()
        self.data = {
            'count_of_tickets': 3,
        }

    def test_create_ticket(self):
        url = reverse('ticket-create', kwargs={'session_pk': self.session.pk, 'date_filter': 'tomorrow'})
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_count_of_ticket(self):
        url = reverse('ticket-create', kwargs={'session_pk': self.session.pk, 'date_filter': 'tomorrow'})
        data = {
            'count_of_tickets': 0,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Count of tickets must be greater than zero!', response.data)

    def test_invalid_day_in_url(self):
        url = reverse('ticket-create', kwargs={'session_pk': self.session.pk, 'date_filter': 'random'})
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Enter correct day in url 'today' or 'tomorrow'", response.data)

    def test_sold_tickets(self):
        AvailableSeatsFactory(session=self.session, date=date.today(), occupied_seats=10)
        url = reverse('ticket-create', kwargs={'session_pk': self.session.pk, 'date_filter': 'today'})
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("All tickets for this session have already been sold!", response.data)

    def test_list_tickets(self):
        TicketFactory(user=self.user)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
