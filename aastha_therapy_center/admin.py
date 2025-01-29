from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    actions = ['approve_appointments', 'reject_appointments']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': ('date', 'time', 'message')
        }),
        ('Status', {
            'fields': ('status', 'admin_note')
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def approve_appointments(self, request, queryset):
        queryset.update(status='approved')
        for appointment in queryset:
            appointment.send_approval_email()
    approve_appointments.short_description = "Approve selected appointments"

    def reject_appointments(self, request, queryset):
        queryset.update(status='rejected')
        for appointment in queryset:
            appointment.send_rejection_email()
    reject_appointments.short_description = "Reject selected appointments"
