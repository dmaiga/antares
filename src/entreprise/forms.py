from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django import forms
from authentication.models import User
from entreprise.models import Entreprise, ServiceEntreprise, NotificationEntreprise,FactureLibre,DemandeService,ServiceRH
from django.utils import timezone
from django import forms
from django_summernote.widgets import SummernoteWidget
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, Entreprise
#22_08

class EntrepriseRegisterForm(forms.ModelForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@entreprise.com'})
    )
    first_name = forms.CharField(
        label="Prénom du représentant",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Nom du représentant",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telephone_pro = forms.CharField(
        label="Téléphone professionnel",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+223 XX XX XX XX'})
    )

    # Champs entreprise
    nom = forms.CharField(
        label="Nom de l'entreprise",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    secteur_activite = forms.CharField(
        label="Secteur d'activité",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Informatique, Finance, Santé...'})
    )
    site_web = forms.URLField(
        label="Site web", 
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.monentreprise.com'}),
        help_text="Exemple: https://www.monentreprise.com"
    )
    description = forms.CharField(
        label="Description de l'entreprise",
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['font', ['strikethrough']],
                    ['para', ['ul', 'ol', 'paragraph']],
                    ['insert', ['link', 'picture', 'video']],
                ],
                'height': '250px',
            }
        }),
        required=False
    )
    adresse = forms.CharField(
        label="Adresse",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ville = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pays = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    taille_entreprise = forms.ChoiceField(
        choices=[
            ('', 'Sélectionnez...'),
            ('1-10', '1 à 10 employés'),
            ('11-50', '11 à 50 employés'),
            ('51-200', '51 à 200 employés'),
            ('200+', 'Plus de 200 employés'),
        ],
        required=False,
        label="Taille de l'entreprise",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    logo = forms.ImageField(
        required=False, 
        label="Logo de l'entreprise",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    accepte_cgv_cgu = forms.BooleanField(
        required=True,
        label="J'accepte les conditions générales d'utilisation",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={
            'required': "Vous devez accepter les conditions pour continuer."
        }
    )

    class Meta:
        model = Entreprise 
        fields = [
            'email', 'first_name', 'last_name', 'telephone_pro',
            'nom', 'secteur_activite', 'site_web', 'description',
            'adresse', 'ville', 'pays', 'taille_entreprise', 'logo',
            'accepte_cgv_cgu'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout des classes Bootstrap aux champs non couverts par les widgets
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                if isinstance(self.fields[field].widget, (forms.Select, forms.SelectMultiple)):
                    self.fields[field].widget.attrs['class'] = 'form-select'
                else:
                    self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_site_web(self):
        site_web = self.cleaned_data.get('site_web', '').strip()
        
        if not site_web:
            return ''
            
        if not site_web.startswith(('http://', 'https://')):
            site_web = 'https://' + site_web
            
        validator = URLValidator()
        try:
            validator(site_web)
        except ValidationError:
            raise forms.ValidationError("Veuillez entrer une URL valide (ex: https://www.monentreprise.com)")
        
        return site_web
    
    def save(self, commit=True):
        # CORRECTION: Créer d'abord le User, puis l'Entreprise
        email_pro = self.cleaned_data['email']
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            email=email_pro,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='entreprise',
            is_active=False  # Inactif jusqu'à validation
        )
        
      
        # Créer l'entreprise
        entreprise = super().save(commit=False)
        entreprise.user = user
        entreprise.nom = self.cleaned_data['nom']
        entreprise.telephone_pro = self.cleaned_data['telephone_pro']
        entreprise.secteur_activite = self.cleaned_data['secteur_activite']
        entreprise.site_web = self.cleaned_data.get('site_web')
        entreprise.description = self.cleaned_data.get('description')
        entreprise.adresse = self.cleaned_data.get('adresse')
        entreprise.ville = self.cleaned_data.get('ville')
        entreprise.pays = self.cleaned_data.get('pays')
        entreprise.taille_entreprise = self.cleaned_data.get('taille_entreprise')
        entreprise.logo = self.cleaned_data.get('logo')
        entreprise.accepte_cgv_cgu = self.cleaned_data['accepte_cgv_cgu']
        
        if commit:
            user.save()
            entreprise.save()
            
        return entreprise   


class CreateEntrepriseForm(forms.ModelForm):
    # Champs utilisateur
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@entreprise.com'})
    )
    first_name = forms.CharField(
        label="Prénom du représentant", 
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Nom du représentant", 
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Champs entreprise (telephone_pro est maintenant dans Entreprise)
    telephone_pro = forms.CharField(
        label="Téléphone professionnel", 
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+223 XX XX XX XX'})
    )
    nom = forms.CharField(
        label="Nom de l'entreprise", 
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    secteur_activite = forms.CharField(
        label="Secteur d'activité", 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Informatique, Finance, Santé...'})
    )
    site_web = forms.CharField(
        label="Site web", 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'https://www.monentreprise.com'}),
        help_text="Exemple: www.monentreprise.com ou https://monentreprise.com"
    )
    description = forms.CharField(
        label="Description", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )
    adresse = forms.CharField(
        label="Adresse", 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ville = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pays = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    taille_entreprise = forms.ChoiceField(
        choices=[
            ('', 'Sélectionnez...'),
            ('1-10', '1 à 10 employés'),
            ('11-50', '11 à 50 employés'),
            ('51-200', '51 à 200 employés'),
            ('200+', 'Plus de 200 employés'),
        ],
        required=False,
        label="Taille de l'entreprise",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    logo = forms.ImageField(
        required=False, 
        label="Logo de l'entreprise",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Entreprise  # CORRECTION: Changer User par Entreprise
        fields = [
            'email', 'first_name', 'last_name', 'telephone_pro',
            'nom', 'secteur_activite', 'site_web', 'description',
            'adresse', 'ville', 'pays', 'taille_entreprise', 'logo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            if field_name not in ['telephone_pro']:  # telephone_pro est déjà configuré
                if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                    field.widget.attrs.setdefault('class', 'form-select')
                else:
                    field.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_site_web(self):
        site_web = self.cleaned_data.get('site_web', '').strip()
        if not site_web:
            return ''
        if not site_web.startswith(('http://', 'https://')):
            site_web = 'https://' + site_web
        validator = URLValidator()
        try:
            validator(site_web)
        except ValidationError:
            raise forms.ValidationError("Veuillez entrer une URL valide (ex: www.monentreprise.com)")
        return site_web

    def save(self, commit=True):
        # Nettoyer les données
        email_pro = self.cleaned_data['email']
        
        # Créer l'utilisateur (SANS telephone_pro car il est dans Entreprise maintenant)
        user = User.objects.create_user(
            email=email_pro,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='entreprise',
            is_active=True
        )
        
        # Créer l'entreprise avec telephone_pro
        entreprise = super().save(commit=False)
        entreprise.user = user
        entreprise.nom = self.cleaned_data['nom']
        entreprise.secteur_activite = self.cleaned_data['secteur_activite']
        entreprise.site_web = self.cleaned_data.get('site_web')
        entreprise.description = self.cleaned_data.get('description')
        entreprise.adresse = self.cleaned_data.get('adresse')
        entreprise.ville = self.cleaned_data.get('ville')
        entreprise.pays = self.cleaned_data.get('pays')
        entreprise.taille_entreprise = self.cleaned_data.get('taille_entreprise')
        entreprise.logo = self.cleaned_data.get('logo')
        entreprise.telephone_pro = self.cleaned_data['telephone_pro']  # CORRECTION: ici maintenant
        entreprise.accepte_cgv_cgu = True
        entreprise.date_acceptation_cgv_cgu = timezone.now()
        entreprise.statut = 'active'
        entreprise.approuvee = True

        if commit:
            user.save()
            entreprise.save()
            
        return entreprise



#22_08
class ServiceEntrepriseForm(forms.ModelForm):
    class Meta:
        model = ServiceEntreprise
        fields = ['titre', 'description', 'prix', 'conditions', 'periodicite_facturation']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            'conditions': forms.Textarea(attrs={'rows': 4}),
            'prix': forms.NumberInput(attrs={'step': '0.01'}),
        }

class DemandeServiceForm(forms.ModelForm):
    class Meta:
        model = DemandeService
        fields = ['service', 'message', 'pieces_jointes']
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Sélectionnez un service...'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Décrivez votre besoin en détail...'
            }),
        }
        labels = {
            'service': "Type de service",
            'message': "Détails de votre demande",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = ServiceRH.objects.all().order_by('nom')

class NotificationEntrepriseForm(forms.ModelForm):
    class Meta:
        model = NotificationEntreprise
        fields = ['titre', 'message', 'niveau', 'action_requise', 'fichier']
        labels = {
            'titre': "Titre",
            'message': "Contenu de la notification",
            'niveau': "Niveau d'alerte",
            'action_requise': "Nécessite une action ?",
            'fichier': "Pièce jointe (facultative)"
        }
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'action_requise': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichier': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_titre(self):
        titre = self.cleaned_data.get('titre', '')
        if titre.lower() in ['notification', 'info']:
            raise forms.ValidationError("Merci de donner un titre plus spécifique.")
        return titre

class FactureLibreForm(forms.ModelForm):
    class Meta:
        model = FactureLibre
        fields = ['titre', 'service', 'description', 'montant_ht', 'tva', 'fichier_facture']
        labels = {
            'titre': "Titre de la facture",
            'description': "Description",
            'montant': "Montant total (FCFA)",
            'fichier_facture': "Fichier de la facture (PDF ou scan)",
        }
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Facture Février 2025'
            }),
            'service': forms.Select(attrs={
                'class': 'form-control',
                'disabled': True 
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Détails des prestations...'
            }),
            'tva': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'onchange': 'calculateTTC()'  # Pour calcul automatique en JS
            }),
            'montant_ht': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'onchange': 'calculateTTC()'
            }),
            'fichier_facture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.png'  # Limite les types de fichiers
            }),
        }

    def clean_montant(self):
        montant = self.cleaned_data['montant']
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return montant

    def clean_fichier_facture(self):
        fichier = self.cleaned_data.get('fichier_facture', False)
        if fichier:
            if fichier.size > 5*1024*1024:  # 5MB max
                raise forms.ValidationError("Le fichier est trop volumineux (> 5MB)")
            return fichier


from django import forms
from .models import DemandeService

class DemandeEditForm(forms.ModelForm):
    class Meta:
        model = DemandeService
        fields = ['statut', 'message']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ajoutez un commentaire si nécessaire...'
            }),
        }


class ContrePropositionForm(forms.ModelForm):
    class Meta:
        model = ServiceEntreprise
        fields = ['contre_proposition']
        widgets = {
            'contre_proposition': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': "Décrivez votre contre-proposition ici..."
            })
        }