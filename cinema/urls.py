from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.LoginPage.as_view(), name='login_page'),
    path('logout/', views.LogoutPage.as_view(), name='logout_page'),
    path('signup/', views.SignupPage.as_view(), name='signup_page'),
    path('create/hall/', views.CinemaHallCreatePage.as_view(), name='create_hall'),
    path('create/session/', views.SessionCreatePage.as_view(), name='create_session'),
    path('create/film/', views.FilmCreatePage.as_view(), name='create_film'),
    path('update/session/<int:pk>/', views.SessionUpdatePage.as_view(), name='update_session'),
    path('update/hall/<int:pk>/', views.HallUpdatePage.as_view(), name='update_hall'),
    path('book/ticket/<int:pk>/<str:date_filter>/', views.TicketBookPage.as_view(), name='book_ticket'),
    path('booked/tickets/', views.BookedTicketsPage.as_view(), name='booked_tickets'),
    path('api/halls/', views.hall_list_api, name='hall_list_api'),
    path('', views.SchedulePage.as_view(), name='schedule_page'),
]