from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from datetime import date, timedelta, datetime
from django.shortcuts import redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import F
from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
)
from cinema.forms import (
    SignUpForm,
    CinemaHallForm,
    SessionForm,
    FilmForm
)
from .models import (
    AvailableSeats,
    CinemaHall,
    Session,
    Ticket,
    Film,
)

User = get_user_model()


# HOME PAGE
class SchedulePage(ListView):
    model = Session
    template_name = 'cinema/schedule.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_filter = self.request.GET.get('date-filter', self.request.session.get('date-filter', 'today'))
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        time_filter = self.request.GET.get('time-filter', 'end_time')
        sold_message = self.request.GET.get('sold_message')

        sessions = Session.objects.all()

        if date_filter == 'today':
            today = date.today()
            now = datetime.now().time()
            sessions = sessions.filter(
                start_date__lte=today,
                end_date__gte=today,
                start_time__gt=now)
        elif date_filter == 'tomorrow':
            tomorrow = date.today() + timedelta(days=1)
            sessions = sessions.filter(start_date__lte=tomorrow, end_date__gte=tomorrow)

        if price_from and price_to:
            sessions = sessions.filter(price__gte=price_from, price__lte=price_to)

        if time_filter == 'end_time':
            sessions = sessions.order_by('-start_time')
        elif time_filter == 'start_time':
            sessions = sessions.order_by('start_time')

        if sold_message:
            messages.error(self.request, 'All tickets for this session have already been sold!')

        context['object_list'] = sessions
        context['date_filter'] = date_filter
        context['time_filter'] = time_filter
        self.request.session['date-filter'] = date_filter

        return context


# LOGIN
class LoginPage(LoginView):
    template_name = 'cinema/login.html'

    def get_success_url(self):
        return reverse_lazy('schedule_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for field in ('username', 'password'):
            context['form'].fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.capitalize()}'
            })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        self.request.user.last_activity = timezone.now()
        self.request.user.save()

        return response


# LOG OUT
class LogoutPage(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('schedule_page')
    login_url = 'login/'


# SIGN UP
class SignupPage(CreateView):
    form_class = SignUpForm
    template_name = 'cinema/signup.html'

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return redirect('schedule_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for field in ('username', 'email', 'password1', 'password2'):
            context['form'].fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.capitalize()}'
            })
        return context


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# CREATE FILM(ADMIN)
class FilmCreatePage(AdminRequiredMixin, CreateView):
    model = Film
    form_class = FilmForm
    template_name = 'cinema/create_film.html'

    def get_success_url(self):
        return reverse_lazy('create_film')

    def form_valid(self, form):
        messages.success(self.request, 'Film successfully created!')
        return super().form_valid(form)


# CREATE HALL(ADMIN)
class CinemaHallCreatePage(AdminRequiredMixin, CreateView):
    model = CinemaHall
    form_class = CinemaHallForm
    template_name = 'cinema/create_hall.html'

    def get_success_url(self):
        return reverse_lazy('create_hall')

    def form_valid(self, form):
        messages.success(self.request, 'Cinema hall successfully created!')
        return super().form_valid(form)


# CREATE SESSION(ADMIN)
class SessionCreatePage(AdminRequiredMixin, CreateView):
    model = Session
    form_class = SessionForm
    template_name = 'cinema/create_session.html'

    def get_success_url(self):
        return reverse_lazy('create_session')

    def form_valid(self, form):
        messages.success(self.request, 'Session successfully created!')
        return super().form_valid(form)


# UPDATE SESSION(ADMIN)
class SessionUpdatePage(AdminRequiredMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'cinema/update_session.html'

    def get_success_url(self):
        messages.success(self.request, 'Session successfully updated!')
        return reverse_lazy('schedule_page')

    def form_valid(self, form):
        session_pk = self.kwargs['pk']

        bought_tickets = Ticket.objects.filter(session__pk=session_pk).count()

        if bought_tickets > 0:
            messages.error(self.request, 'Tickets have already been booked for this session!')
            return redirect('schedule_page')

        return super().form_valid(form=form)


# UPDATE HALL(ADMIN)
class HallUpdatePage(AdminRequiredMixin, UpdateView):
    model = CinemaHall
    form_class = CinemaHallForm
    template_name = 'cinema/update_hall.html'

    def get_success_url(self):
        messages.success(self.request, 'Hall successfully updated!')
        return reverse_lazy('schedule_page')

    def form_valid(self, form):
        hall_pk = self.kwargs['pk']
        today = date.today()

        bought_tickets = Ticket.objects.filter(session__hall__pk=hall_pk, session__end_date__gt=today).count()

        if bought_tickets > 0:
            messages.error(self.request, 'Tickets have already been booked in this hall!')
            return redirect('schedule_page')

        return super().form_valid(form=form)


# LIST OF HALLS (JSON)
def hall_list_api(request):
    halls = CinemaHall.objects.values('id', 'name')
    return JsonResponse({'halls': list(halls)})


# BOOK TICKETS(USER)
class TicketBookPage(LoginRequiredMixin, CreateView):
    login_url = 'login/'
    model = Ticket
    fields = ['count_of_tickets']
    template_name = 'cinema/book_tickets.html'

    def get_success_url(self):
        messages.success(self.request, f'The tickets was successfully booked for!')
        return reverse_lazy('schedule_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = Session.objects.get(pk=self.kwargs['pk'])
        data_filter = self.kwargs['date_filter']
        available_seats = session.available_tomorrow() if data_filter == 'tomorrow' else session.available_today()

        context['session'] = session
        context['available_seats'] = available_seats
        return context

    def form_valid(self, form):
        session_pk = self.kwargs['pk']
        session = Session.objects.get(pk=session_pk)
        count_of_tickets = form.cleaned_data['count_of_tickets']
        date_filter = self.kwargs['date_filter']
        available_seats = session.available_tomorrow() if date_filter == 'tomorrow' else session.available_today()
        user = self.request.user

        if count_of_tickets <= 0:
            messages.error(self.request, "Count of tickets must be greater than zero!")
            return redirect('schedule_page')

        if available_seats < count_of_tickets:
            messages.error(self.request, 'Not enough available seats!')
            return redirect('schedule_page')

        session_date = date.today() + timedelta(days=1) if date_filter == 'tomorrow' else date.today()

        available_seats_obj, created = AvailableSeats.objects.get_or_create(session=session, date=session_date)
        available_seats_obj.occupied_seats += count_of_tickets
        available_seats_obj.save()

        total_price = count_of_tickets * session.price
        self.request.user.total_spent = F('total_spent') + total_price

        self.object = form.save(commit=False)
        self.object.user = user
        self.object.session = session
        self.object.count_of_tickets = count_of_tickets
        self.object.total_price = total_price
        self.object.data_session = session_date
        self.object.save()

        return super().form_valid(form=form)


# BOOKED TICKETS(USER)
class BookedTicketsPage(LoginRequiredMixin, ListView):
    login_url = 'login/'
    model = Ticket
    template_name = 'cinema/booked_tickets.html'
    paginate_by = 5

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)