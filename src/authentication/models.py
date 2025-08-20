from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class BaseProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='%(class)s_profile')
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True)
    telephone_perso = models.CharField(
        max_length=20, 
        blank=True, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Format de numéro invalide.")]
    )
    date_naissance = models.DateField(null=True, blank=True)
    contact_urgence = models.CharField(max_length=100, blank=True)
    quartier = models.CharField(max_length=100, blank=True)
    rue = models.CharField(max_length=50, blank=True)
    porte = models.CharField(max_length=50, blank=True)
    ville = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

class EmployeeProfile(BaseProfile):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('pause', 'En pause'),
        ('termine', 'Terminé'),
    ]
    CONTRACT_CHOICES = [
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('stage', 'Stage'),
        ('interim', 'Intérim'),
    ]

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    telephone_pro = models.CharField(
        max_length=20, 
        blank=True, 
        validators=[RegexValidator(r'^\+?\s*(?:\d[\s\-()]?){8,}$', message="Format de numéro invalide.")]
    )
    fiche_poste = models.ForeignKey('todo.FichePoste', null=True, blank=True, on_delete=models.SET_NULL, related_name='users')
    poste_occupe = models.CharField(max_length=100, blank=True)
    contract_type = models.CharField(max_length=10, choices=CONTRACT_CHOICES, blank=True)
    department = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='subordinates')
    skills = models.ManyToManyField(Skill, blank=True)
    notes = models.TextField(blank=True)
    last_evaluation = models.DateField(null=True, blank=True)
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0, message="Le salaire ne peut pas être négatif.")]
    )
    working_hours = models.CharField(max_length=50, blank=True)
    remote_days = models.PositiveIntegerField(default=0)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)

    def __str__(self):
        return f"Profil employé de {self.user.get_full_name()}"


from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email doit être renseignée")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('rh', 'Ressources Humaines'),
        ('employe', 'Employé'),
        ('stagiaire', 'Stagiaire'),
        ('entreprise', 'Entreprise'),
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
    ]

    email = models.EmailField(unique=True, error_messages={'unique': "Cet email est déjà utilisé."})
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None  # Désactiver username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # pas de champs obligatoires en plus

    objects = UserManager()  # <<< ICI on utilise notre manager

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        
        if creating and self.role:  # Seulement à la création
            group, _ = Group.objects.get_or_create(name=self.role)
            self.groups.add(group)



