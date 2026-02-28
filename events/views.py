from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import Event, Registration
from .recommendation import get_recommendations
import io
import urllib, base64
from collections import Counter
import qrcode
from django.http import HttpResponse
import csv
from django.utils import timezone
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .forms import StudentProfileForm
from .models import UserProfile

def home(request):
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')

    events = Event.objects.all().order_by('date')

    if query:
        events = events.filter(title__icontains=query)

    if selected_category:
        events = events.filter(category=selected_category)

    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user)

    all_events = Event.objects.all()
    total_events = all_events.count()
    total_capacity = sum(event.capacity for event in all_events)
    total_registered = sum(event.registered_count() for event in all_events)

    category_choices = Event.CATEGORY_CHOICES

    return render(request, 'home.html', {
        'events': events,
        'recommendations': recommendations,
        'total_events': total_events,
        'total_capacity': total_capacity,
        'total_registered': total_registered,
        'category_choices': category_choices,
        'selected_category': selected_category,
        'query': query,
    })

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('/')


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check event capacity
    if event.seats_left() <= 0:
        messages.error(request, "Event is full.")
        return redirect('/')

    # Prevent duplicate registration
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.error(request, "You have already registered for this event.")
        return redirect('/')

    # Ensure user profile exists
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Check if required student details are missing
    profile_incomplete = not all([
        profile.college_email,
        profile.registration_number,
        profile.branch,
        profile.department,
        profile.year_of_study,
    ])

    # If profile is incomplete, collect details first
    if profile_incomplete:
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()

                # Proceed with registration after saving profile
                Registration.objects.create(user=request.user, event=event)

                send_mail(
                    'Event Registration Confirmation',
                    f'You have successfully registered for {event.title}',
                    'admin@college.com',
                    [request.user.email],
                    fail_silently=True,
                )

                messages.success(request, "Profile saved and event registered successfully!")
                return redirect('/')
        else:
            form = StudentProfileForm(instance=profile)

        return render(request, 'register_event_form.html', {
            'form': form,
            'event': event
        })

    # If profile already complete, register directly
    Registration.objects.create(user=request.user, event=event)

    send_mail(
        'Event Registration Confirmation',
        f'You have successfully registered for {event.title}',
        'admin@college.com',
        [request.user.email],
        fail_silently=True,
    )

    messages.success(request, "Successfully registered! Confirmation email sent.")
    return redirect('/')


@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(user=request.user)
    return render(request, 'my_registrations.html', {'registrations': registrations})

@login_required
def analytics_dashboard(request):
    if not request.user.is_staff:
        return render(request, 'unauthorized.html', status=403)
    events = Event.objects.all()
    registrations = Registration.objects.all()

    total_events = events.count()
    total_registrations = registrations.count()

    categories = [event.category for event in events]
    category_counts = Counter(categories)

    # Create chart
    fig, ax = plt.subplots()
    ax.bar(category_counts.keys(), category_counts.values())
    ax.set_title("Event Category Distribution")

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graph = base64.b64encode(image_png).decode('utf-8')
    graph = urllib.parse.quote(graph)

    return render(request, 'analytics.html', {
        'total_events': total_events,
        'total_registrations': total_registrations,
        'graph': graph
    })

@login_required
def generate_qr(request, registration_id):
    registration = get_object_or_404(
        Registration,
        registration_id=registration_id,
        user=request.user
    )

    qr_data = str(registration.registration_id)
    qr = qrcode.make(qr_data)

    import io
    import base64

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return render(request, 'qr_view.html', {
        'registration': registration,
        'qr_base64': qr_base64,
    })

@login_required
def export_registrations_csv(request):
    if not request.user.is_staff:
        return render(request, 'unauthorized.html', status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registrations.csv"'

    writer = csv.writer(response)
    writer.writerow([
    'Username',
    'College Email',
    'Registration Number',
    'Branch',
    'Department',
    'Year of Study',
    'Event Title',
    'Category',
    'Date',
    'Venue',
    'Attendance',
    'Verified At',
    'Verified By',
    'Registration ID'
])

    registrations = Registration.objects.select_related('user', 'event').all()

    for reg in registrations:
        profile = getattr(reg.user, 'userprofile', None)

    writer.writerow([
        reg.user.username,
        getattr(profile, 'college_email', '') if profile else '',
        getattr(profile, 'registration_number', '') if profile else '',
        getattr(profile, 'branch', '') if profile else '',
        getattr(profile, 'department', '') if profile else '',
        getattr(profile, 'year_of_study', '') if profile else '',
        reg.event.title,
        reg.event.category,
        reg.event.date,
        reg.event.venue,
        reg.attended,
        reg.verified_at,
        reg.verified_by.username if reg.verified_by else '',
        reg.registration_id
    ])

    return response

@login_required
def verify_qr(request):
    # Allow only staff/admin to verify entries
    if not request.user.is_staff:
        return render(request, 'unauthorized.html', status=403)

    result = None
    error = None

    if request.method == 'POST':
        raw_input = request.POST.get('registration_id', '').strip()

        # Extract UUID even if scanned text contains extra words
        uuid_match = re.search(
            r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
            raw_input
        )

        if not uuid_match:
            error = "Invalid QR format. UUID not found."
            return render(request, 'verify_qr.html', {'result': None, 'error': error})

        registration_id = uuid_match.group(0)

        try:
            reg = Registration.objects.select_related('user', 'event').get(registration_id=registration_id)

            if reg.attended:
                result = {
                    'status': 'already_verified',
                    'registration': reg
                }
            else:
                reg.attended = True
                reg.verified_at = timezone.now()
                reg.verified_by = request.user
                reg.save()

                result = {
                    'status': 'verified_success',
                    'registration': reg
                }

        except Registration.DoesNotExist:
            error = "Invalid QR / Registration ID not found."

    return render(request, 'verify_qr.html', {
        'result': result,
        'error': error
    })