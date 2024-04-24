from rest_framework.authtoken import views
from django.urls import path, include
from rest_framework import routers
from api.views import (
    SessionCreateView,
    SessionUpdateView,
    TicketCreateView,
    SessionListView,
    FilmCreateView,
    HallCreateView,
    HallUpdateView,
    TicketListView,
    AuthViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register('', AuthViewSet, basename='auth')

urlpatterns = [
    path('auth/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('session/create/', SessionCreateView.as_view(), name='session-create'),
    path('session/update/<int:pk>/', SessionUpdateView.as_view(), name='session-update'),
    path('film/create/', FilmCreateView.as_view(), name='film-create'),
    path('hall/create/', HallCreateView.as_view(), name='hall-create'),
    path('hall/update/<int:pk>/', HallUpdateView.as_view(), name='hall-update'),
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('sessions/<int:session_pk>/book/<str:date_filter>/', TicketCreateView.as_view(), name='ticket-create'),
]