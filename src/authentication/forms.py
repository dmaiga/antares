# authentication/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, EmployeeProfile, Skill
from todo.models import FichePoste

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

# -----------------------------
# Création d'un utilisateur
# -----------------------------
class CreateUserForm(forms.ModelForm):
    fiche_poste_modele = forms.ModelChoiceField(
        queryset=FichePoste.objects.filter(is_modele=True),
        required=False,
        label="Modèle de fiche de poste"
    )
    poste_occupe = forms.CharField(max_length=100, required=False)
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    telephone_pro = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['email', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Créer le profil si l'utilisateur est employé ou stagiaire
            if self.cleaned_data['role'] in ['employe', 'stagiaire']:
                EmployeeProfile.objects.create(
                    user=user,
                    fiche_poste=self.cleaned_data.get('fiche_poste_modele'),
                    poste_occupe=self.cleaned_data.get('poste_occupe', ''),
                    start_date=self.cleaned_data.get('start_date'),
                    telephone_pro=self.cleaned_data.get('telephone_pro', '')
                )
        return user

# -----------------------------
# Formulaire mise à jour profil RH
# -----------------------------
class RHUserUpdateForm(forms.ModelForm):
    skills_list = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2 form-control'}),
        label="Compétences"
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            'poste_occupe', 'department', 'start_date', 'end_date',
            'statut', 'contract_type', 'manager', 'salary',
            'working_hours', 'remote_days', 'notes',
            'cv', 'contract_file', 'photo'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['skills_list'].initial = self.instance.skills.all()

    def save(self, commit=True):
        profile = super().save(commit)
        if commit:
            profile.skills.set(self.cleaned_data.get('skills_list', []))
            profile.save()
        return profile

# -----------------------------
# Formulaire mise à jour profil personnel
# -----------------------------
class PersonalUserUpdateForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = [
            'photo', 'telephone_pro', 'telephone_perso', 'date_naissance',
            'contact_urgence', 'quartier', 'rue', 'porte', 'ville',
            'poste_occupe'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def save(self, commit=True):
        profile = super().save(commit)
        if commit:
            profile.save()
        return profile

# -----------------------------
# Formulaire FichePoste (inchangé)
# -----------------------------
class FichePosteForm(forms.ModelForm):
    class Meta:
        model = FichePoste
        fields = ['titre']
        labels = {'titre': 'Nom du modèle de fiche'}


class RHUserBasicForm(forms.ModelForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = EmployeeProfile
        fields = ['statut', 'poste_occupe', 'department', 'start_date', 'end_date']
