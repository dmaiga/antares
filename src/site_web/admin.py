from django.contrib import admin
from .models import  Mission,ConsultantQuickApplication

from django.db import models



class MissionInline(admin.TabularInline):
    model = Mission
    extra = 1

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("name", "experience", "consultant")
    search_fields = ("name", "consultant__first_name", "consultant__last_name")

@admin.register(ConsultantQuickApplication)
class ConsultantQuickApplicationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'first_name', 'last_name', 'email', 'experience', 'enrollment_type', 'created_at']
    list_filter = ['enrollment_type', 'experience', 'created_at']
    search_fields = ['reference', 'first_name', 'last_name', 'email']
    readonly_fields = ['reference']