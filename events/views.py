from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import Event, Registration
from .recommendation import get_recommendations
import matplotlib.pyplot as plt
import io
import urllib, base64
from collections import Counter
import qrcode
from django.http import HttpResponse


def home(request):
    query = request.GET.get('q')
    events = Event.objects.all().order_by('date')

    if query:
        events = events.filter(title__icontains=query)

    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user)

    return render(request, 'home.html', {
        'events': events,
        'recommendations': recommendations
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

    # Check if event is full
    if event.seats_left() <= 0:
        messages.error(request, "Event is full.")
        return redirect('/')

    # Prevent duplicate registration
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.error(request, "You have already registered for this event.")
        return redirect('/')

    Registration.objects.create(user=request.user, event=event)

    # Send confirmation email (console backend for now)
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

    qr_data = f"User: {registration.user.username}, Event: {registration.event.title}, ID: {registration.registration_id}"

    qr = qrcode.make(qr_data)

    response = HttpResponse(content_type="image/png")
    qr.save(response, "PNG")
    return response