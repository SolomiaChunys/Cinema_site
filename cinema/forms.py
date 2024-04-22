from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import CinemaHall, Session, Film

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Film Name',
            }),
            'genre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Film Genre',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }


class CinemaHallForm(forms.ModelForm):
    class Meta:
        model = CinemaHall
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Name of Hall',
            }),
            'size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Size of Hall',
                'min': '1',
            }),
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = '__all__'

        widgets = {
            'film': forms.Select(attrs={
                'class': 'form-select',
            }),
            'hall': forms.Select(attrs={
                'class': 'form-select',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Session Price',
                'min': '0',
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Session Start-Time',
                'type': 'time',
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Session End-Time',
                'type': 'time',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Session Start-Date',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Session End-Date',
                'type': 'date',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        hall = cleaned_data.get('hall')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        price = cleaned_data.get('price')

        session = Session.objects.filter(
            hall=hall,
            start_date__lte=end_date,
            end_date__gte=start_date,
            start_time__lte=end_time,
            end_time__gte=start_time,
        ).exclude(pk=self.instance.pk)

        if session.exists():
            times = session.values_list('start_time', 'end_time')
            times_string = [f'{str(start_time)[:-3]}-{str(end_time)[:-3]}'
                            for start_time, end_time in times]
            raise ValidationError(f"This hall has a session for that time: {times_string[0]}")

        if start_date > end_date:
            raise ValidationError("Start date must be before end date.")

        if price < 0:
            raise ValidationError("Price cannot be negative.")
