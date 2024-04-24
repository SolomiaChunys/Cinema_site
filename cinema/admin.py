from django.contrib import admin  # MiaGames16
from cinema import models

admin.site.register(models.User)
admin.site.register(models.CinemaHall)
admin.site.register(models.Film)
admin.site.register(models.Session)
admin.site.register(models.Ticket)
admin.site.register(models.AvailableSeats)