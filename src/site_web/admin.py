from django.contrib import admin
from .models import  Mission,ConsultantQuickApplication

from django.db import models



class MissionInline(admin.TabularInline):
    model = Mission
    extra = 1

@admin.register(ConsultantQuickApplication)
class ConsultantQuickApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'expertise', 'experience', 'created_at')
    inlines = [MissionInline]

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("name", "experience", "consultant")
    search_fields = ("name", "consultant__first_name", "consultant__last_name")
