from django.shortcuts import render, get_object_or_404, redirect,HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Appointment
import json


# Create your views here.

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'sections/about.html')

def blog(request):
    page = request.GET.get('page', '1')
    return render(request, 'sections/blog.html', {'page': page})

def services(request):
    return render(request, 'sections/services.html')

def hypnotherapy(request):
    return render(request, 'hypnotherapy_service_detail.html')

def appointment(request):
    return render(request, 'sections/appointments.html')

def book_appointment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create appointment in database
            appointment = Appointment.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                date=data['date'],
                time=data['time'],
                message=data.get('message', '')
            )
            print('Appointment saved:', appointment)
            
            try:
                # Send email to admin
                admin_html = render_to_string('emails/admin_notification.html', {
                    'appointment': appointment
                })
                admin_text = strip_tags(admin_html)
                
                admin_email = EmailMultiAlternatives(
                    subject='New Appointment Request',
                    body=admin_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.EMAIL_HOST_USER]
                )
                admin_email.attach_alternative(admin_html, "text/html")
                admin_email.send()
                print('Admin email sent')

                # Send confirmation to user
                user_html = render_to_string('emails/user_confirmation.html', {
                    'name': appointment.name,
                    'date': appointment.date,
                    'time': appointment.time
                })
                user_text = strip_tags(user_html)
                
                user_email = EmailMultiAlternatives(
                    subject='Appointment Confirmation - Astha Therapy Center',
                    body=user_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[appointment.email]
                )
                user_email.attach_alternative(user_html, "text/html")
                user_email.send()
                print('User email sent')
                
            except Exception as email_error:
                print('Email Error:', str(email_error))
                # Continue even if email fails
            
            return JsonResponse({
                'status': 'success',
                'message': 'Appointment booked successfully!'
            })
            
        except Exception as e:
            print('Error:', str(e))
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })
