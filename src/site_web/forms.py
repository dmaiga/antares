from django import forms
from .models import ContactRequest
from django_summernote.widgets import SummernoteWidget

class ExpertContactForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['first_name', 'last_name', 'company', 'sector', 'phone', 'email', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optionnel'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optionnel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com'
            }),
            'company': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'nom entreprise'
            }),
            'sector': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "Secteur d'activité"
            }),
            'phone': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '+223 XX XX XX XX/00223 XX XX XX XX'
            }),

            'message': SummernoteWidget(attrs={
                'placeholder': "Décrivez votre besoin précis pour que notre expert puisse vous répondre efficacement...",
                'summernote': {
                    'width': '100%',
                    'height': '300px',
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline', 'clear']],
                        ['para', ['ul', 'ol']],
                       
                    ]
                }
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['message'].required = True
        self.instance.contact_type = 'expert'


from django import forms
from .models import ContactRequest
from django_summernote.widgets import SummernoteWidget

class GeneralContactForm(forms.ModelForm):
    SUBJECT_CHOICES = [
        ('info', 'Demande d\'information'),
        ('rdv', 'Prise de rendez-vous'),
        ('service', 'Demande de service'),
        ('autre', 'Autre demande'),
    ]
    
    subject = forms.ChoiceField(
        choices=[('', 'Sélectionnez un motif')] + SUBJECT_CHOICES,
        required=True,
        label="Objet de votre demande",
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    accept_conditions = forms.BooleanField(
        label="J'accepte que mes données soient utilisées pour traiter ma demande",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'privacyCheck'
        }),
        error_messages={
            'required': "Vous devez accepter les conditions pour soumettre le formulaire"
        }
    )
    class Meta:
        model = ContactRequest
        fields = ['first_name', 'last_name', 'email', 'subject', 'message','accept_conditions']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optionnel'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optionnel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com'
            }),
            'message': SummernoteWidget(attrs={
                'summernote': {
                    'width': '100%',
                    'height': '300px',
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline', 'clear']],
                        ['para', ['ul', 'ol']],
                        ['insert', ['link']],
                        ['view', ['codeview']]
                    ],
                    'placeholder': 'Décrivez votre demande en détail...',
                }
            }),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'message': 'Votre message',
        }
        help_texts = {
            'email': 'Nous vous répondrons à cette adresse',
            'first_name': 'Champ facultatif',
            'last_name': 'Champ facultatif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.contact_type = 'general'
        
        # Rendre les champs nom/prénom non obligatoires
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Ajoutez ici des validations personnalisées si nécessaire
        return email

    def get_subject_display(self):
        """Méthode pour obtenir la version lisible du sujet"""
        subject_mapping = dict(self.SUBJECT_CHOICES)
        return subject_mapping.get(self.cleaned_data['subject'], self.cleaned_data['subject'])
        
#14_08   
from django import forms
from django.forms import inlineformset_factory
from .models import ConsultantQuickApplication,Mission
from django.core.validators import FileExtensionValidator
import re  

class ConsultantQuickEnrollmentForm(forms.ModelForm):
    cv = forms.FileField(
        label="CV (PDF uniquement)",
        required=False,
        validators=[FileExtensionValidator(['pdf'])],
        widget=forms.FileInput(attrs={
            'accept': '.pdf',
            'class': 'form-control',
            'id': 'cv-upload'  # Ajout d'un ID pour le JavaScript
        })
    )
    
    personal_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Ex : Disponible à partir de septembre, recherche missions courtes...'
        }),
        label="Message complémentaire"
    )
    
    class Meta:
        model = ConsultantQuickApplication
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'expertise', 'experience', 'cv', 'personal_message'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@professionnel.com'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+223 XX XX XX XX',
                'pattern': r'^\+?[\d\s]{10,}$',
                'class': 'form-control'
            }),
            'expertise': forms.TextInput(attrs={
                'placeholder': 'Ex: Transformation digitale RH',
                'class': 'form-control',
                'list': 'expertise-suggestions'  # Pour les suggestions
            }),
            'experience': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'experience': "Années d'expérience*",
            'first_name': "Prénom*",
            'last_name': "Nom*",
            'email': "Email professionnel*",
            'phone': "Téléphone*",
            'expertise': "Domaine d'expertise*"
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Nettoyage du numéro
        phone = re.sub(r'[^\d+]', '', phone)
        if not re.match(r'^\+?[\d]{10,15}$', phone):
            raise forms.ValidationError("Format de téléphone invalide. Exemple: +223XXXXXXXX")
        return phone

class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['name', 'experience', 'details']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Audit RH, Migration ERP',
                'required': 'required'
            }),
            'experience': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Décrivez votre expérience (technologies utilisées, durée, etc.)'
            }),
            'DELETE': forms.HiddenInput(),
            'id': forms.HiddenInput()
        }
        labels = {
            'name': 'Mission*',
            'experience': 'Votre expérience sur cette mission*',
            'details': 'Détails complémentaires'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des choix d'expérience si nécessaire
        self.fields['experience'].widget.attrs.update({
            'class': 'form-select mission-experience'
        })

MissionFormSet = inlineformset_factory(
    ConsultantQuickApplication,
    Mission,
    form=MissionForm,
    extra=3,   
    max_num=3  
)

#18_08
from django import forms
from django.contrib.auth.forms import UserCreationForm
from authentication.models import User
from candidats.models import ProfilCandidat
from django.core.validators import RegexValidator
from django.utils import timezone

class InscriptionCandidatForm(UserCreationForm):
    telephone = forms.CharField(
        max_length=20,
        required=False,
        validators=[RegexValidator(r'^\+?\s*(?:\d[\s\-()]?){8,}$')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+223XXXXXXXX'
        })
    )
    
    cgu_acceptees = forms.BooleanField(
        required=True,
        error_messages={'required': 'Vous devez accepter les CGU'},
        label="J'accepte les conditions générales"
    )
    
    accepte_newsletter = forms.BooleanField(
        required=False,
        label="Recevoir les newsletters"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'telephone', 
                 'password1', 'password2', 'cgu_acceptees', 'accepte_newsletter']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer le champ role
        self.fields['role'] = forms.CharField(
            initial='candidat',
            widget=forms.HiddenInput()
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'candidat'
        user.username = user.email  # Pour compatibilité
        
        if commit:
            user.save()
            # Créer le profil candidat avec toutes les données
            ProfilCandidat.objects.create(
                user=user,
                telephone=self.cleaned_data.get('telephone', ''),
                
                accepte_newsletter=self.cleaned_data.get('accepte_newsletter', False),
                cgu_acceptees=self.cleaned_data.get('cgu_acceptees', False),
                date_inscription=timezone.now()
            )
        return user
    
#