from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True, help_text="Admin notes about this appointment")

    def __str__(self):
        return f"Appointment for {self.name} on {self.date} at {self.time} ({self.status})"

    def save(self, *args, **kwargs):
        # Check if status has changed to approved
        if self.pk:  # If this is an existing appointment
            old_appointment = Appointment.objects.get(pk=self.pk)
            if old_appointment.status != 'approved' and self.status == 'approved':
                self.send_approval_email()
            elif old_appointment.status != 'rejected' and self.status == 'rejected':
                self.send_rejection_email()
        
        super().save(*args, **kwargs)

    def send_approval_email(self):
        try:
            # Send confirmation email to user
            context = {
                'name': self.name,
                'date': self.date,
                'time': self.time,
                'admin_note': self.admin_note
            }
            
            html_content = render_to_string('emails/appointment_approved.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject='Your Appointment has been Approved - Astha Therapy Center',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            print(f"Approval email sent to {self.email}")
            
        except Exception as e:
            print(f"Error sending approval email: {str(e)}")

    def send_rejection_email(self):
        try:
            context = {
                'name': self.name,
                'date': self.date,
                'time': self.time,
                'admin_note': self.admin_note
            }
            
            html_content = render_to_string('emails/appointment_rejected.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject='Update on Your Appointment - Astha Therapy Center',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            print(f"Rejection email sent to {self.email}")
            
        except Exception as e:
            print(f"Error sending rejection email: {str(e)}")

    class Meta:
        ordering = ['-created_at']
