from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


def get_and_authenticate_user(username, password):
    user = authenticate(
        username=username,
        password=password
    )
    if user is None:
        raise serializers.ValidationError("Invalid username/password. Please try again!")
    return user


def create_user_account(username, email, password, first_name="", last_name="", **extra_fields):
    user = get_user_model().objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        **extra_fields
    )
    user.is_active = True
    user.save()
    return user
