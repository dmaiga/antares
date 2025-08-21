
from django import forms
from django.contrib import admin
from .models import JobOffer

class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = '__all__'
        widgets = {
            'secteur': forms.Select(choices=JobOffer.SectorChoices.choices),
        }

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    form = JobOfferForm
    list_display = ['reference', 'titre', 'secteur', 'statut', 'date_publication']
    list_filter = ['secteur', 'statut', 'type_offre', 'date_publication']
    search_fields = ['titre', 'reference', 'societe']