from django.contrib import admin
from .models import Event, Registration
from .models import UserProfile

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'capacity')
    search_fields = ('title', 'venue')
    list_filter = ('date',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'attended', 'verified_at', 'verified_by')
    search_fields = ('user__username', 'event__title', 'registration_id')
    list_filter = ('attended', 'event__category')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'interests')