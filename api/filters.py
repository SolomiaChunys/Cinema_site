from rest_framework.exceptions import ValidationError
from datetime import date, timedelta
from rest_framework import filters


class SessionFilters(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        date_filter = request.query_params.get('date-filter', 'today')

        price_from = request.query_params.get('price_from')
        price_to = request.query_params.get('price_to')

        hall_id = request.query_params.get('hall_id')

        time_from = request.query_params.get('time_from')
        time_to = request.query_params.get('time_to')

        # Filter by data(today, tomorrow)
        if date_filter != 'tomorrow' and date_filter != 'today':
            raise ValidationError("Enter correct day in url date_filter 'today' or 'tomorrow'")

        if date_filter == 'today':
            today = date.today()
            queryset = queryset.filter(start_date__lte=today, end_date__gte=today)
        elif date_filter == 'tomorrow':
            tomorrow = date.today() + timedelta(days=1)
            queryset = queryset.filter(start_date__lte=tomorrow, end_date__gte=tomorrow)

        # Filter by price(from, to)
        if price_from and price_to:
            queryset = queryset.filter(price__gte=price_from, price__lte=price_to)

        # Filter by hall
        if hall_id:
            queryset = queryset.filter(hall__id=hall_id)

        # Filter by time(from, to)
        if time_from and time_to:
            queryset = queryset.filter(start_time__gte=time_from, start_time__lte=time_to)

        return queryset
