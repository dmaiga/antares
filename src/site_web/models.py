from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class ContactRequest(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('general', 'Demande générale'),
        ('expert', 'Demande expert'),
    ]
    
    SUBJECT_CHOICES = [
        ('info', 'Demande d\'information'),
        ('rdv', 'Prise de rendez-vous'),
        ('service', 'Demande de service'),
        ('autre', 'Autre demande'),
    ]

    # Champs communs
    contact_type = models.CharField(max_length=50, choices=CONTACT_TYPE_CHOICES)
    first_name = models.CharField("Prénom", max_length=150, blank=True)
    last_name = models.CharField("Nom", max_length=150, blank=True)
    email = models.EmailField(max_length=150, unique=False)
    message = models.TextField(max_length=5000)
    
    # Champs spécifiques aux experts
    company = models.CharField("Entreprise", max_length=150, blank=True)
    sector = models.CharField("Secteur", max_length=250, blank=True)
    phone = models.CharField(
        "Téléphone",
        max_length=20,
        blank=True,
        validators=[RegexValidator(regex=r'^\+?[\d\s]{10,20}$')],
        help_text="Format : +223 XX XXX XXX ou 00223XXXXXXXX"
    )
    
    # Champs spécifiques généraux
    subject = models.CharField("Objet",max_length=250,choices=SUBJECT_CHOICES,blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Demande de contact")
        verbose_name_plural = _("Demandes de contact")
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_contact_type_display()} - {self.email}"
    


#________________________________________________________
#14_08

from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from datetime import datetime
from authentication.models import User
import uuid
class ConsultantQuickApplication(models.Model):
    class ExperienceLevel(models.TextChoices):
        JUNIOR = 'junior', '1-3 ans'
        CONFIRMED = 'confirmed', '4-6 ans'
        SENIOR = 'senior', '7-9 ans'
        EXPERT = 'expert', '10+ ans'
    
    # Informations de base (obligatoires)
    first_name = models.CharField("Prénom*", max_length=100)
    last_name = models.CharField("Nom*", max_length=100)
    email = models.EmailField("Email professionnel*")
    phone = models.CharField("Téléphone*", max_length=20)
    
    # Expertise (obligatoire)
    expertise = models.CharField("Domaine d'expertise*", max_length=200)
    experience = models.CharField(
        "Niveau d'expérience*",
        max_length=10,
        choices=ExperienceLevel.choices
    )
    
    # Fichier (obligatoire mais peut être ajouté plus tard)
    cv = models.FileField(
        "CV (PDF uniquement)*",
        upload_to='consultants/cvs/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf'])],
        blank=True,
        null=True
    )
    
    # Message facultatif
    personal_message = models.TextField(
        "Message personnel (facultatif)",
        blank=True,
        null=True,
        help_text="Laissez-nous un message si vous souhaitez ajouter des informations"
    )
    #reference
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Utilisateur associé"
    )
    reference = models.CharField("Référence", max_length=20, unique=True, blank=True)
    enrollment_type = models.CharField(
        "Type d'enregistrement",
        max_length=50,
        choices=[('consultant', 'Consultant'), ('candidate', 'Candidat')],
        default='candidate'
    )
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    profile_complete = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Inscription rapide"
        verbose_name_plural = "Inscriptions rapides"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.expertise}) - {self.reference}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            short_uuid = str(uuid.uuid4())[:8].upper()  # 8 caractères
            self.reference = f"ANT{short_uuid}"
        
        # CORRECTION: cohérence avec les choix du champ
        if self.experience == self.ExperienceLevel.EXPERT:
            self.enrollment_type = 'consultant'
        else:
            self.enrollment_type = 'candidate' 
            
        super().save(*args, **kwargs)



#15_08
class Mission(models.Model):
    class MissionExperience(models.TextChoices):
        JUNIOR = 'junior', '1-3 ans'
        CONFIRMED = 'confirmed', '4-6 ans'
        SENIOR = 'senior', '7-9 ans'
        EXPERT = 'expert', '10+ ans'
        
    consultant = models.ForeignKey(
        ConsultantQuickApplication,
        on_delete=models.CASCADE,
        related_name="missions"
    )
    name = models.CharField("Nom de la mission", max_length=200)
    experience = models.CharField(
        "Expérience sur cette mission",
        max_length=10,
        choices=MissionExperience.choices
    )
    details = models.TextField("Détails", blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_experience_display()}"
# 15_08    

from django.db import models
from django.core.validators import FileExtensionValidator, URLValidator
from taggit.managers import TaggableManager

class ConsultantApplication(models.Model):
    class MissionExperience(models.TextChoices):
        JUNIOR = 'junior', 'Junior (1-3 ans)'
        CONFIRMED = 'confirmed', 'Confirmé (3-5 ans)'
        SENIOR = 'senior', 'Senior (5-10 ans)'
        EXPERT = 'expert', 'Expert (10+ ans)'
    
    # 1. Informations personnelles
    first_name = models.CharField("Prénom*", max_length=100)
    last_name = models.CharField("Nom*", max_length=100)
    email = models.EmailField("Email professionnel*")
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    location = models.CharField("Localisation", max_length=100, blank=True)
    mobility = models.CharField(
        "Mobilité",
        max_length=20,
        choices=[
            ('locale', 'Locale'),
            ('nationale', 'Nationale'), 
            ('internationale', 'Internationale')
        ],
        blank=True
    )
    nationality = models.CharField("Nationalité", max_length=50, blank=True)
    
    # 2. Domaines d'intervention et expertises
    expertise = models.TextField("Domaine principal d'expertise*")
    intervention_domains = models.TextField(
        "Domaines d'intervention",
        blank=True,
        help_text="Listez les types de missions sur lesquelles vous pourriez être affecté"
    )
    
    # 3. Expériences missions
    missions_data = models.JSONField("Expériences missions", default=list)
    
    # 4. Compétences
    competencies = TaggableManager("Compétences techniques", blank=True)
    
    # 5. Disponibilité
    availability_status = models.CharField(
        "Disponibilité",
        max_length=20,
        choices=[
            ('immediate', 'Disponible immédiatement'),
            ('delayed', 'Disponible sous X jours')
        ],
        blank=True
    )
    availability_days = models.PositiveIntegerField(
        "Jours avant disponibilité",
        blank=True,
        null=True
    )
    mission_type_preference = models.CharField(
        "Type de mission préféré",
        max_length=20,
        choices=[
            ('full_time', 'Temps plein'),
            ('part_time', 'Temps partiel'),
            ('short_term', 'Courte durée'),
            ('long_term', 'Longue durée')
        ],
        blank=True
    )
    max_duration = models.PositiveIntegerField(
        "Durée maximum (mois)",
        blank=True,
        null=True
    )
    
    # 6. Documents et réseaux
    cv = models.FileField(
        "CV",
        upload_to='consultants/cvs/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])],
        blank=True
    )
    linkedin = models.URLField("LinkedIn", blank=True, validators=[URLValidator()])
    portfolio = models.URLField("Portfolio", blank=True, validators=[URLValidator()])
    certifications = models.TextField("Certifications", blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField("Date de création", auto_now_add=True)
    is_approved = models.BooleanField("Approuvé", default=False)

    class Meta:
        verbose_name = "Candidature Consultant"
        verbose_name_plural = "Candidatures Consultants"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
from django.db import models
from django.core.validators import FileExtensionValidator
