from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('register/<int:event_id>/', views.register_event, name='register'),
    path('my-events/', views.my_registrations, name='my_events'),
]