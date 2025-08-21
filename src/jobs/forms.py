from django import forms
from django.forms import DateInput
from .models import JobOffer
from django_summernote.widgets import SummernoteWidget

class JobOfferForm(forms.ModelForm):
    # Utilisez Summernote pour tous les champs de contenu
    mission_principale = forms.CharField(
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['para', ['ul', 'ol', 'paragraph', 'style']],
                    ['insert', ['link', 'hr']],
                    ['view', ['fullscreen', 'codeview', 'help']]
                ],
                'height': '200px',
                'styleWithSpan': False,
            }
        }),
        label="Missions principales",
        required=False
    )
    
    taches = forms.CharField(
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['para', ['ul', 'ol', 'paragraph', 'style']],
                    ['insert', ['link', 'hr']],
                    ['view', ['fullscreen', 'codeview', 'help']]
                ],
                'height': '300px',
                'styleWithSpan': False,
            }
        }),
        label="Tâches",
        required=False
    )

    
    competences_qualifications = forms.CharField(
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['para', ['ul', 'ol', 'paragraph', 'style']],
                    ['insert', ['link', 'hr']],
                    ['view', ['fullscreen', 'codeview', 'help']]
                ],
                'height': '200px',
                'styleWithSpan': False,
            }
        }),
        label="Compétences qualifications",
        required=False
    )
    
    conditions = forms.CharField(
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['para', ['ul', 'ol', 'paragraph', 'style']],
                    ['insert', ['link', 'hr']],
                    ['view', ['fullscreen', 'codeview', 'help']]
                ],
                'height': '200px',
                'styleWithSpan': False,
            }
        }),
        label="Conditions",
        required=False
    )
    
    profil_recherche = forms.CharField(
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['para', ['ul', 'ol', 'paragraph', 'style']],
                    ['insert', ['link', 'hr']],
                    ['view', ['fullscreen', 'codeview', 'help']]
                ],
                'height': '200px',
                'styleWithSpan': False,
            }
        }),
        label="Profil recherché",
        required=False
    )
    
    comment_postuler = forms.CharField(
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['para', ['ul', 'ol', 'paragraph', 'style']],
                    ['insert', ['link', 'hr']],
                    ['view', ['fullscreen', 'codeview', 'help']]
                ],
                'height': '200px',
                'styleWithSpan': False,
            }
        }),
        label="Comment postuler",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Common attributes
        for field in self.fields.values():
            field.required = False
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput, SummernoteWidget)):
                field.widget.attrs.setdefault('class', 'form-control')
        
        # Configuration spécifique pour nombre_candidat (TextField)
        self.fields['nombre_candidat'].widget.attrs.update({
            'placeholder': '1, Beaucoup, Plusieurs, etc.',
            'class': 'form-control'
        })
        
        self.fields['secteur'].widget.attrs.update({
            'class': 'form-select select2'  
        })
        
        # Specific attributes
        self.fields['visible_sur_site'].widget.attrs['class'] = 'form-check-input'
        self.fields['date_publication'].widget = DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['date_limite'].widget = DateInput(attrs={'type': 'date', 'class': 'form-control'})

    class Meta:
        model = JobOffer
        fields = '__all__'
        exclude = ['auteur', 'date_creation', 'date_mise_a_jour', 'statut']
        help_texts = {
            'reference': "Format: ANT/STA/00002025",
            'fichier_pdf': "PDF optionnel (max. 5MB)",
            'nombre_candidat': "Nombre Candidat EX: '1','Plusieurs', '2 à 3'",
            'secteur': "Sélectionnez le secteur d'activité principal",
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data