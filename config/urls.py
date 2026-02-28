from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from events import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('my-events/', views.my_registrations, name='my_registrations'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('qr/<uuid:registration_id>/', views.generate_qr, name='generate_qr'),
    path('export-csv/', views.export_registrations_csv, name='export_csv'),
    path('verify-qr/', views.verify_qr, name='verify_qr'),
    path('chatbot/', views.chatbot_reply, name='chatbot_reply'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
