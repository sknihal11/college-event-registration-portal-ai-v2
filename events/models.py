from django.db import models
from django.contrib.auth.models import User
import uuid

class Event(models.Model):

    CATEGORY_CHOICES = [
        ('seminar', 'Seminar'),
        ('workshop', 'Workshop'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='seminar')
    capacity = models.IntegerField(default=100)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def registered_count(self):
        return self.registration_set.count()

    def seats_left(self):
        return self.capacity - self.registered_count()

    def __str__(self):
        return self.title


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    attended = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_registrations'
    )

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class UserProfile(models.Model):
    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Comma separated interests (e.g., seminar, sports)"
    )

    college_email = models.EmailField(blank=True, null=True)
    registration_number = models.CharField(max_length=30, blank=True, null=True, unique=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.user.username