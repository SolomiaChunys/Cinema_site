from api.utils import get_and_authenticate_user, create_user_account
from rest_framework import generics, permissions, viewsets, status
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model, logout
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers
from api.filters import SessionFilters
from datetime import date, timedelta
from django.db.models import F
from api.serializers import (
    UserRegisterSerializer,
    CinemaHallSerializer,
    TicketBookSerializer,
    UserLoginSerializer,
    AuthUserSerializer,
    SessionSerializer,
    TicketSerializer,
    EmptySerializer,
    FilmSerializer,
)
from cinema.models import (
    AvailableSeats,
    CinemaHall,
    Session,
    Ticket,
    Film,
)

User = get_user_model()


# LIST SESSION(ALL)
class SessionListView(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [OrderingFilter, SessionFilters]


# CREATE SESSION(ADMIN)
class SessionCreateView(generics.CreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAdminUser]


# UPDATE SESSION(ADMIN)
class SessionUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        session_pk = self.kwargs['pk']
        bought_tickets = Ticket.objects.filter(session__pk=session_pk).count()

        if bought_tickets > 0:
            raise ValidationError('Tickets have already been booked for this session!')

        return super().perform_update(serializer)


# CREATE FILM(ADMIN)
class FilmCreateView(generics.CreateAPIView):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    permission_classes = [permissions.IsAdminUser]


# CREATE HALL(ADMIN)
class HallCreateView(generics.CreateAPIView):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer
    permission_classes = [permissions.IsAdminUser]


# UPDATE HALL(ADMIN)
class HallUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        hall_pk = self.kwargs['pk']
        bought_tickets = Ticket.objects.filter(session__hall__pk=hall_pk).count()

        if bought_tickets > 0:
            raise ValidationError('Tickets have already been booked in this hall!')

        return super().perform_update(serializer)


# CREATE TICKET(USER)
class TicketCreateView(generics.CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketBookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        session_pk = self.kwargs['session_pk']
        session = Session.objects.get(pk=session_pk)
        count_of_tickets = serializer.validated_data.get('count_of_tickets')
        date_filter = self.kwargs['date_filter']
        available_seats = session.available_tomorrow() if date_filter == 'tomorrow' else session.available_today()
        user = self.request.user

        if date_filter != 'tomorrow' and date_filter != 'today':
            raise serializers.ValidationError("Enter correct day in url 'today' or 'tomorrow'")

        if count_of_tickets is None:
            raise serializers.ValidationError("Enter value for 'count_of_tickets'!")

        if count_of_tickets <= 0:
            raise serializers.ValidationError("Count of tickets must be greater than zero!")

        if available_seats == 0:
            raise serializers.ValidationError('All tickets for this session have already been sold!')

        if available_seats < count_of_tickets:
            raise serializers.ValidationError('Not enough available seats!')

        session_date = date.today() + timedelta(days=1) if date_filter == 'tomorrow' else date.today()

        if session.start_date > session_date or session.end_date < session_date:
            raise serializers.ValidationError(
                f'There is not session on this date! Available dates {session.start_date} to {session.end_date}'
            )

        available_seats_obj, created = AvailableSeats.objects.get_or_create(session=session, date=session_date)
        available_seats_obj.occupied_seats += count_of_tickets
        available_seats_obj.save()

        total_price = count_of_tickets * session.price
        User.objects.filter(pk=user.pk).update(total_spent=F('total_spent') + total_price)

        serializer.save(
            user=user,
            session=session,
            count_of_tickets=count_of_tickets,
            total_price=total_price,
            data_session=session_date
        )


# LIST TICKET(USER)
class TicketListView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)


# AUTHENTICATION
class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny, ]
    serializer_class = EmptySerializer
    serializer_classes = {
        'login': UserLoginSerializer,
        'register': UserRegisterSerializer
    }

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        logout(request)
        data = {'success': 'Successfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()