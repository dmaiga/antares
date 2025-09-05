# authentication/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, EmployeeProfile
from todo.models import FichePoste
from django_summernote.widgets import SummernoteWidget
# -----------------------------
# Formulaire de connexion
# -----------------------------
# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
class LoginForm(AuthenticationForm):
    # Remplacer username par email
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre@email.com',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe',
            'autocomplete': 'current-password'
        })
    )
    
    # Supprimer le champ username par défaut
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            self.user_cache = authenticate(
                self.request, 
                username=email,  # Utiliser email comme username
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Email ou mot de passe incorrect",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


from django import forms
from .models import User, EmployeeProfile

# -----------------------------
# Formulaire de création d'utilisateur (RH seulement)
# -----------------------------
from django.contrib.auth.hashers import make_password
import secrets
import string
class CreateUserForm(forms.ModelForm):
    ROLE_CHOICES_LIMITED = [
        ('employe', 'Employé'),
        ('stagiaire', 'Stagiaire'),
        ('rh', 'Ressources Humaines'),
       
    ]
    
    # Champs obligatoires minimaux
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@entreprise.com'}),
        label="Email professionnel*"
    )
    
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
        label="Prénom*"
    )
    
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
        label="Nom*"
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES_LIMITED,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rôle*"
    )

    poste_occupe = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Développeur Python'}),
        label="Poste occupé*"
    )
    
    fiche_poste = forms.ModelChoiceField(
        queryset=FichePoste.objects.filter(is_modele=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Modèle de fiche de poste"
    )
    
    department = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: IT, RH, Commercial...'}),
        label="Département*"
    )
    
    contract_type = forms.ChoiceField(
        choices=EmployeeProfile.CONTRACT_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Type de contrat*"
    )
    
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date d'embauche*"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generated_password = None

    def generate_random_password(self, length=10):
        """Génère un mot de passe aléatoire simple"""
        import secrets
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for i in range(length))

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Utiliser les prénom et nom fournis dans le formulaire
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Générer mot de passe
        self.generated_password = 'pass123'
        user.set_password(self.generated_password)
        
        if commit:
            user.save()
            
            # Créer le profil employé avec les données professionnelles
            EmployeeProfile.objects.create(
                user=user,
                poste_occupe=self.cleaned_data.get('poste_occupe'),
                department=self.cleaned_data.get('department'),
                contract_type=self.cleaned_data.get('contract_type'),
                start_date=self.cleaned_data.get('start_date'),
                email_pro=self.cleaned_data.get('email'),
                statut='actif'
            )
            
        return user
    

# -----------------------------
# Formulaire utilisateur (modification par l'utilisateur)
# -----------------------------
class EmployeeProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = [
            # Informations personnelles
            'photo', 'telephone_perso', 'date_naissance',
            'contact_urgence', 'quartier', 'rue', 'porte', 'ville',
            
            # Informations professionnelles de contact
            'telephone_pro', 'email_pro', 'bureau',
            
            # Compétences et formation
            'competences', 'competences_soft',
            'niveau_etude', 'domaine_etude', 'annees_experience','cv',
            
            # Poste (lecture seule pour information)
            'poste_occupe'
        ]
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'cv': forms.FileInput(attrs={'class': 'form-control'}),
            'telephone_perso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+223 XX XX XX XX'}),
            'telephone_pro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+223 XX XX XX XX'}),
            'email_pro': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email.professionnel@entreprise.ml'}),
            'bureau': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bureau A12'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact_urgence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom et téléphone'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quartier'}),
            'rue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rue'}),
            'porte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N°'}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'poste_occupe': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'competences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Compétences techniques séparées par des virgules (ex: Python, Django, SQL)'
            }),
            'competences_soft': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Compétences comportementales (ex: Communication, Leadership)'
            }),
            'niveau_etude': forms.Select(attrs={'class': 'form-select'}),
            'domaine_etude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domaine d\'étude'}),
            'annees_experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre tous les champs optionnels sauf ceux requis
        for field in self.fields:
            self.fields[field].required = False
        
        # Champ poste_occupe en lecture seule pour information
        self.fields['poste_occupe'].disabled = True
        self.fields['poste_occupe'].help_text = "Contactez les RH pour modifier votre poste"

# -----------------------------
# Formulaire RH (modification par RH/Admin)
# -----------------------------
from django import forms
from .models import EmployeeProfile, User
from django import forms
from .models import EmployeeProfile, User

class RHProfileForm(forms.ModelForm):
    ROLE_CHOICES_LIMITED = [
        ('employe', 'Employé'),
        ('stagiaire', 'Stagiaire'),
        ('rh', 'Ressources Humaines'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES_LIMITED,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rôle*",
        required=True
    )
    
    class Meta:
        model = EmployeeProfile
        fields = [
            'statut', 'contract_type', 'department', 'poste_occupe', 'start_date', 'end_date',
            'salaire_brut', 'cv', 'contract_file', 'niveau_etude', 'domaine_etude',
            'annees_experience', 'competences', 'competences_soft', 'photo', 'telephone_pro'
        ]
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: IT, RH, Commercial...'}),
            'poste_occupe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Développeur Python'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salaire_brut': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cv': forms.FileInput(attrs={'class': 'form-control'}),
            'contract_file': forms.FileInput(attrs={'class': 'form-control'}),
            'niveau_etude': forms.Select(attrs={'class': 'form-select'}),
            'domaine_etude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domaine de formation'}),
            'annees_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'competences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Compétences techniques...'}),
            'competences_soft': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Compétences comportementales...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'telephone_pro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+223 XX XX XX XX'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def clean_poste_occupe(self):
        poste_occupe = self.cleaned_data.get('poste_occupe')
        statut = self.cleaned_data.get('statut')
        if statut == 'actif' and not poste_occupe:
            raise forms.ValidationError("Le poste occupé est requis pour un employé actif.")
        return poste_occupe

    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.user and 'role' in self.cleaned_data:
            # Toujours sauvegarder le rôle choisi
            self.user.role = self.cleaned_data['role']
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
            
        return profile
    


class FichePosteForm(forms.ModelForm):
    class Meta:
        model = FichePoste
        fields = ['titre']
        labels = {
            'titre': 'Nom du modèle de fiche',
        }