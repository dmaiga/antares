from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
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
        ('consultant', 'Consultant'),
        ('candidat', 'Candidat'),
    ]

    email = models.EmailField(unique=True, error_messages={'unique': "Cet email est déjà utilisé."})
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        
        if creating and self.role:
            group, _ = Group.objects.get_or_create(name=self.role)
            self.groups.add(group)



class EmployeeProfile(models.Model):
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
        ('consultant', 'Consultant'),
        ('essai', 'Période d\'essai'),
    ]
    
    EDUCATION_CHOICES = [
        ('bac', 'Baccalauréat'),
        ('bac2', 'Bac+2 (BTS, DUT)'),
        ('bac3', 'Bac+3 (Licence)'),
        ('bac5', 'Bac+5 (Master)'),
        ('doctorat', 'Doctorat'),
        ('autre', 'Autre'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employeeprofile')
    
    # --- Identification de base ---
    matricule = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    # --- Informations personnelles (optionnelles) ---
    telephone_perso = models.CharField(max_length=20, blank=True, verbose_name="Téléphone personnel")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    contact_urgence = models.CharField(max_length=100, blank=True, verbose_name="Contact d'urgence")
    quartier = models.CharField(max_length=100, blank=True, verbose_name="Quartier")
    rue = models.CharField(max_length=50, blank=True, verbose_name="Rue")
    porte = models.CharField(max_length=50, blank=True, verbose_name="Porte/N°")
    ville = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Photo")

    # --- Informations de contact professionnel ---
    email_pro = models.EmailField(blank=True, verbose_name="Email professionnel")
    telephone_pro = models.CharField(max_length=20, blank=True, verbose_name="Téléphone professionnel")
    bureau = models.CharField(max_length=50, blank=True, verbose_name="Bureau/Poste de travail")
    
    # --- Informations professionnelles critiques ---
    poste_occupe = models.CharField(max_length=100, blank=True, verbose_name="Poste occupé")
    department = models.CharField(max_length=100, blank=True, verbose_name="Département/Service")
    site = models.CharField(max_length=100, blank=True, verbose_name="Site/Lieu de travail")
    
    # --- Dates importantes ---
    start_date = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin de contrat")
    date_integration = models.DateField(null=True, blank=True, verbose_name="Date d'intégration")
    
    # --- Statut et contrat ---
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='candidat', verbose_name="Statut")
    contract_type = models.CharField(max_length=10, choices=CONTRACT_CHOICES, blank=True, verbose_name="Type de contrat")
    
    # --- Données analytiques RH ---
    niveau_etude = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True, verbose_name="Niveau d'étude")
    domaine_etude = models.CharField(max_length=100, blank=True, verbose_name="Domaine d'étude")
    annees_experience = models.PositiveIntegerField(null=True, blank=True, verbose_name="Années d'expérience")
    salaire_brut = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Salaire brut mensuel")
    cout_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, 
                                   verbose_name="Coût total mensuel", help_text="Salaire + charges + avantages")
    
    # --- Compétences et évaluations ---
    competences = models.TextField(blank=True, verbose_name="Compétences techniques",
                                 help_text="Compétences séparées par des virgules")
    competences_soft = models.TextField(blank=True, verbose_name="Compétences comportementales")
    
    # --- Suivi RH ---
    notes_rh = models.TextField(blank=True, verbose_name="Notes RH internes")
    points_forts = models.TextField(blank=True, verbose_name="Points forts")
    axes_amelioration = models.TextField(blank=True, verbose_name="Axes d'amélioration")
    
    
    # --- Indicateurs de performance ---
    taux_absenteeisme = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux d'absentéisme (%)")
    productivite = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Indice de productivité")
    satisfaction = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Niveau de satisfaction")
    
    # --- Fichiers et documents ---
    cv = models.FileField(upload_to='cvs/%Y/%m/', blank=True, null=True, verbose_name="CV")
    contract_file = models.FileField(upload_to='contracts/%Y/%m/', blank=True, null=True, verbose_name="Contrat de travail")
    documents = models.FileField(upload_to='documents/%Y/%m/', blank=True, null=True, verbose_name="Autres documents")
    
    # --- Métadonnées ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True, verbose_name="Actif dans le système")
    
    # --- Relations ---
    fiche_poste = models.ForeignKey('todo.FichePoste', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Profil Employé"
        verbose_name_plural = "Profils Employés"
        ordering = ['-created_at']

    def __str__(self):
        if self.user.get_full_name():
            return f"{self.user.get_full_name()} - {self.poste_occupe or 'Sans poste'}"
       
        else:
            return f"Employé #{self.id} - {self.poste_occupe or 'Sans poste'}"

   