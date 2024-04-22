from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import password_validation
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework import serializers
from cinema.models import (
    CinemaHall,
    Film,
    Session,
    Ticket,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'total_spent',
        ]


class CinemaHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemaHall
        fields = [
            'id',
            'name',
            'size',
        ]


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = [
            'id',
            'name',
            'genre',
            'image'
        ]


class SessionSerializer(serializers.ModelSerializer):
    film = serializers.PrimaryKeyRelatedField(queryset=Film.objects.all())
    hall = serializers.PrimaryKeyRelatedField(queryset=CinemaHall.objects.all())

    class Meta:
        model = Session
        fields = [
            'id',
            'film',
            'hall',
            'price',
            'start_time',
            'end_time',
            'start_date',
            'end_date',
        ]
        extra_kwargs = {
            'start_time': {'required': True},
            'end_time': {'required': True},
            'start_date': {'required': True},
            'end_date': {'required': True},
        }

    def validate(self, data):
        hall = data['hall']
        start_date = data['start_date']
        end_date = data['end_date']
        start_time = data['start_time']
        end_time = data['end_time']
        price = data['price']

        session = Session.objects.filter(
            hall=hall,
            start_date__lte=end_date,
            end_date__gte=start_date,
            start_time__lte=end_time,
            end_time__gte=start_time,
        ).exclude(pk=getattr(self.instance, 'pk', None))

        if session.exists():
            times = session.values_list('start_time', 'end_time')
            times_string = [f'{str(start_time)[:-3]}-{str(end_time)[:-3]}'
                            for start_time, end_time in times]
            raise serializers.ValidationError(f"This hall has a session for that time: {times_string[0]}")

        if start_date > end_date:
            raise serializers.ValidationError("Start date must be before end date.")

        if price < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return data


class TicketBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['count_of_tickets']


class TicketSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    session = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all())

    class Meta:
        model = Ticket

        fields = [
            'id',
            'user',
            'session',
            'total_price',
            'data_session',
            'count_of_tickets',
        ]


# Authentication
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'auth_token',
        )
        read_only_fields = ('id', 'is_active', 'is_staff')

    def get_auth_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class EmptySerializer(serializers.Serializer):
    pass


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name'
        )
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_username(self, value):
        user = User.objects.filter(username=value)
        if user:
            raise serializers.ValidationError("Username is already taken")
        return value

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if user:
            raise serializers.ValidationError("Email is already taken")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value
