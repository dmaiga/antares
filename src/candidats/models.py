from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from simple_history.models import HistoricalRecords
from jobs.models import JobOffer

# ====================================================
# CONSTANTES DE CHOIX
# ====================================================
GENRE_CHOICES = [
    ('M', 'Masculin'),
    ('F', 'Féminin'),
]

NIVEAU_CHOICES = [
    ('CAP_BEP', 'CAP / BEP'),
    ('BAC', 'Baccalauréat'),
    ('BAC+2', 'Bac+2 (BTS, DUT)'),
    ('BAC+3', 'Licence'),
    ('BAC+4', 'Master 1'),
    ('BAC+5', 'Master 2'),
    ('DOC', 'Doctorat'),
    ('AUTRE', 'Autre'),
]

TYPE_ETABLISSEMENT_CHOICES = [
    ('UNIV', 'Université'),
    ('ECOLE', 'École'),
    ('LYCEE', 'Lycée'),
    ('CFA', 'Centre de formation'),
    ('AUTRE', 'Autre'),
]

TYPE_CONTRAT_CHOICES = [
    ('CDI', 'CDI'),
    ('CDD', 'CDD'),
    ('STAGE', 'Stage'),
    ('ALTERNANCE', 'Alternance'),
    ('FREELANCE', 'Freelance'),
    ('INTERIM', 'Intérim'),
    ('APPRENTISSAGE', 'Apprentissage'),
]

SECTEUR_CHOICES = [
    ('IT', 'Informatique/Télécoms'),
    ('SANTE', 'Santé'),
    ('BANQUE', 'Banque/Assurance'),
    ('COMMERCE', 'Commerce'),
    ('INDUSTRIE', 'Industrie'),
    ('EDUCATION', 'Éducation'),
    ('CONSULTING', 'Consulting'),
    ('AUTRE', 'Autre'),
]

TYPE_DOCUMENT_CHOICES = [
    ('CV', 'Curriculum Vitae'),
    ('LM', 'Lettre de motivation'),
    ('DIPLOME', 'Diplôme'),
    ('RECOMMANDATION', 'Lettre de recommandation'),
    ('PORTFOLIO', 'Portfolio'),
    ('CERTIFICAT', 'Certificat'),
    ('AUTRE', 'Autre document'),
]

LANGUE_CHOICES = [
    ('FR', 'Français'),
    ('EN', 'Anglais'),
    ('ES', 'Espagnol'),
    ('DE', 'Allemand'),
    ('IT', 'Italien'),
    ('AUTRE', 'Autre'),
]

STATUT_CANDIDATURE_CHOICES = [
    ('BROUILLON', 'Brouillon'),
    ('POSTULE', 'Postulé'),
    ('RELANCE', 'Relancé'),
    ('ENTRETIEN1', '1er entretien'),
    ('ENTRETIEN2', '2ème entretien'),
    ('ENTRETIEN3', '3ème entretien'),
    ('OFFRE', 'Offre reçue'),
    ('ACCEPTE', 'Accepté'),
    ('REFUSE', 'Refusé'),
    ('RETIRE', 'Retiré'),
]

CANAL_CANDIDATURE_CHOICES = [
    ('SITE', 'Site carrière'),
    ('LINKEDIN', 'LinkedIn'),
    ('INDEED', 'Indeed'),
    ('APEC', 'APEC'),
    ('POLE_EMPLOI', 'Pôle emploi'),
    ('COOPTATION', 'Cooptation'),
    ('RESEAU', 'Réseau personnel'),
    ('AUTRE', 'Autre'),
]

TYPE_ENTRETIEN_CHOICES = [
    ('PHONE', 'Téléphonique'),
    ('VIDEO', 'Visioconférence'),
    ('PRESENTIEL', 'Présentiel'),
    ('TEST', 'Test technique'),
]

STATUT_ENTRETIEN_CHOICES = [
    ('PLANIFIE', 'Planifié'),
    ('CONFIRME', 'Confirmé'),
    ('TERMINE', 'Terminé'),
    ('ANNULE', 'Annulé'),
    ('REPORTE', 'Reporté'),
]

COMPETENCE_CATEGORIES = [
    ('HARD', 'Hard Skill'),
    ('SOFT', 'Soft Skill'),
    ('LANGUE', 'Langue'),
    ('AUTRE', 'Autre'),
]

# ====================================================
# MODÈLES DE BASE
# ====================================================
class SoftDeleteModel(models.Model):
    """
    Modèle abstrait pour implémenter la suppression logique (soft delete)
    """
    est_supprime = models.BooleanField(default=False, verbose_name="Est supprimé")
    date_suppression = models.DateTimeField(null=True, blank=True, verbose_name="Date de suppression")
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Marque l'objet comme supprimé sans le supprimer physiquement"""
        self.est_supprime = True
        self.date_suppression = timezone.now()
        self.save()
    
    def restore(self):
        """Restaure un objet précédemment supprimé"""
        self.est_supprime = False
        self.date_suppression = None
        self.save()

class Adresse(models.Model):
    ligne1 = models.CharField(null=True, blank=True, max_length=255, verbose_name="Adresse ligne 1")
    code_postal = models.CharField(max_length=10, null=True, blank=True, verbose_name="Code Postal")
    ville = models.CharField(null=True, blank=True, max_length=100, verbose_name="Ville")
    pays = models.CharField(null=True, blank=True, max_length=100, default="France", verbose_name="Pays")
    
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
    
    def __str__(self):
        return f"{self.ligne1}, {self.code_postal} {self.ville}"

# ====================================================
# MODÈLES PRINCIPAUX
# ====================================================
class Competence(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la compétence")
    categorie = models.CharField(max_length=20, choices=COMPETENCE_CATEGORIES, default='AUTRE')
    description = models.TextField(blank=True)
    est_supprime = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def soft_delete(self):
        self.est_supprime = True
        self.save()

class ProfilCandidat(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='profil_candidat')
    photo = models.ImageField(upload_to='candidat/avatars/', null=True, blank=True, verbose_name="Photo de profil")
    competences = models.ManyToManyField(Competence, blank=True, related_name="candidats")
    telephone = models.CharField(max_length=20, validators=[RegexValidator(r'^\+?\s*(?:\d[\s\-()]?){8,}$')], blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES, blank=True)
    
    adresse = models.ForeignKey(Adresse, on_delete=models.SET_NULL, null=True, blank=True)
    
    salaire_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salaire minimum souhaité")
    salaire_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salaire maximum souhaité")
    
    linkedin_url = models.URLField(blank=True, verbose_name="Profil LinkedIn")
    portfolio_url = models.URLField(blank=True, verbose_name="Portfolio")
    recherche_active = models.BooleanField(default=True, verbose_name="En recherche active")
    date_debut_recherche = models.DateField(null=True, blank=True, verbose_name="Date de début de recherche")
    
    accepte_newsletter = models.BooleanField(default=False)
    cgu_acceptees = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True, verbose_name="Disponible immédiatement")
    mobilite_geographique = models.BooleanField(default=False)
    rayon_mobilite = models.PositiveIntegerField(null=True, blank=True, default=50, verbose_name="Rayon de mobilité (km)")
    
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_maj = models.DateTimeField(auto_now=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    
    class Meta:
        verbose_name = "Profil Candidat"
        verbose_name_plural = "Profils Candidats"
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"
    
    @property
    def fourchette_salariale(self):
        if self.salaire_min and self.salaire_max:
            return f"{self.salaire_min} - {self.salaire_max} €"
        elif self.salaire_min:
            return f"À partir de {self.salaire_min} €"
        elif self.salaire_max:
            return f"Jusqu'à {self.salaire_max} €"
        return "Non spécifié"

class Diplome(models.Model):
    candidat = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diplomes')
    intitule = models.CharField(max_length=200)
    etablissement = models.CharField(max_length=200)
    type_etablissement = models.CharField(max_length=10, choices=TYPE_ETABLISSEMENT_CHOICES, default='UNIV')
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    domaine = models.CharField(max_length=100)
    
    pays_obtention = models.CharField(max_length=100, default="France", verbose_name="Pays d'obtention")
    ville_obtention = models.CharField(max_length=100, blank=True, verbose_name="Ville d'obtention")
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_obtention = models.DateField()
    mention = models.CharField(max_length=50, blank=True, verbose_name="Mention")
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Note/20")
    description = models.TextField(blank=True)
    competences = models.ManyToManyField(Competence, blank=True, related_name="diplomes")
    
    est_supprime = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Diplôme"
        verbose_name_plural = "Diplômes"
        ordering = ['-date_obtention']
    
    def __str__(self):
        return f"{self.intitule} ({self.etablissement})"
    
    @property
    def duree_etudes(self):
        if self.date_debut and self.date_obtention:
            return (self.date_obtention - self.date_debut).days // 365
        return None
    
    def clean(self):
        if self.date_debut and self.date_obtention and self.date_obtention < self.date_debut:
            raise ValidationError("La date d'obtention ne peut pas être antérieure à la date de début.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        self.est_supprime = True
        self.save()

class ExperienceProfessionnelle(models.Model):
    candidat = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='experiences')
    poste = models.CharField(max_length=200)
    entreprise = models.CharField(max_length=200)
    secteur = models.CharField(max_length=20, choices=SECTEUR_CHOICES, default='AUTRE')
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT_CHOICES, default='CDI')
    
    lieu = models.CharField(max_length=200)
    pays = models.CharField(max_length=100, default="France")
    remote = models.BooleanField(default=False, verbose_name="Télétravail")
    
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    en_poste = models.BooleanField(default=False)
    
    salaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Salaire annuel")
    equipe = models.PositiveIntegerField(null=True, blank=True, verbose_name="Taille de l'équipe")
    description = models.TextField()
    competences = models.ManyToManyField(Competence, blank=True, related_name="experiences")
    realisation = models.TextField(blank=True, verbose_name="Réalisations marquantes")
    
    manager = models.CharField(max_length=100, blank=True, verbose_name="Manager/Référent")
    contact_reference = models.CharField(max_length=200, blank=True, verbose_name="Contact de référence")
    
    est_supprime = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Expérience professionnelle"
        verbose_name_plural = "Expériences professionnelles"
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.poste} chez {self.entreprise}"
    
    @property
    def duree(self):
        if self.en_poste:
            end_date = timezone.now().date()
        elif self.date_fin:
            end_date = self.date_fin
        else:
            return None
            
        return (end_date - self.date_debut).days // 30
    
    def clean(self):
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")
        if self.en_poste and self.date_fin:
            raise ValidationError("Vous ne pouvez pas avoir une date de fin si vous êtes toujours en poste.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        self.est_supprime = True
        self.save()

def document_path(instance, filename):
    return f'documents/candidat_{instance.candidat.id}/{instance.type_document}/{filename}'

class Document(models.Model):
    candidat = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=20, choices=TYPE_DOCUMENT_CHOICES)
    fichier = models.FileField(upload_to=document_path)
    nom = models.CharField(max_length=200)
    
    version = models.PositiveIntegerField(default=1, verbose_name="Version")
    langue = models.CharField(max_length=10, choices=LANGUE_CHOICES, default='FR')
    description = models.TextField(blank=True)
    mots_cles = models.CharField(max_length=255, blank=True, verbose_name="Mots-clés")
    
    est_public = models.BooleanField(default=False, verbose_name="Visible par les recruteurs")
    est_actif = models.BooleanField(default=True, verbose_name="Document actif")
    est_modele = models.BooleanField(default=False, verbose_name="Modèle de document")
    
    date_upload = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)
    taille_fichier = models.PositiveIntegerField(editable=False, verbose_name="Taille du fichier (octets)")
    
    est_supprime = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-date_upload']
        unique_together = ['candidat', 'nom', 'version']
    
    def __str__(self):
        return f"{self.nom} v{self.version} ({self.get_type_document_display()})"
    
    def save(self, *args, **kwargs):
        if self.fichier:
            self.taille_fichier = self.fichier.size
        super().save(*args, **kwargs)
    
    @property
    def taille_formattee(self):
        if self.taille_fichier < 1024:
            return f"{self.taille_fichier} o"
        elif self.taille_fichier < 1024 * 1024:
            return f"{self.taille_fichier / 1024:.1f} Ko"
        else:
            return f"{self.taille_fichier / (1024 * 1024):.1f} Mo"
    
    def soft_delete(self):
        self.est_supprime = True
        self.save()

class Candidature(models.Model):
    candidat = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidatures')
    offre = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    
    date_postulation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, choices=STATUT_CANDIDATURE_CHOICES, default='POSTULE')
    canal = models.CharField(max_length=20, choices=CANAL_CANDIDATURE_CHOICES, default='SITE')
    
    cv_utilise = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='cv_candidatures')
    lettre_motivation = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='lm_candidatures')
    documents_supplementaires = models.ManyToManyField(Document, blank=True, related_name='candidatures_supp')
    
    notes = models.TextField(blank=True)
    motivation = models.TextField(blank=True, verbose_name="Motivation pour ce poste")
    points_forts = models.TextField(blank=True, verbose_name="Points forts pour ce poste")
    points_faibles = models.TextField(blank=True, verbose_name="Points à améliorer")
    
    nombre_relances = models.PositiveIntegerField(default=0, verbose_name="Nombre de relances")
    date_derniere_relance = models.DateTimeField(null=True, blank=True, verbose_name="Date dernière relance")
    
    est_supprime = models.BooleanField(default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        unique_together = ('candidat', 'offre')
        ordering = ['-date_postulation']
    
    def __str__(self):
        return f"{self.candidat.get_full_name()} - {self.offre.titre}"
    
    @property
    def delai_reponse(self):
        if self.statut in ['ACCEPTE', 'REFUSE', 'RETIRE']:
            return (self.date_mise_a_jour - self.date_postulation).days
        return None
    
    def soft_delete(self):
        self.est_supprime = True
        self.save()

class Entretien(models.Model):
    candidature = models.ForeignKey(Candidature, on_delete=models.CASCADE, related_name='entretiens')
    type_entretien = models.CharField(max_length=20, choices=TYPE_ENTRETIEN_CHOICES, default='PRESENTIEL')
    statut = models.CharField(max_length=20, choices=STATUT_ENTRETIEN_CHOICES, default='PLANIFIE')
    
    date_prevue = models.DateTimeField(verbose_name="Date prévue")
    duree_prevue = models.PositiveIntegerField(default=60, verbose_name="Durée prévue (minutes)")
    date_reelle = models.DateTimeField(null=True, blank=True, verbose_name="Date réelle")
    duree_reelle = models.PositiveIntegerField(null=True, blank=True, verbose_name="Durée réelle (minutes)")
    
    interlocuteurs = models.TextField(verbose_name="Interlocuteur(s)")
    poste_interlocuteurs = models.TextField(blank=True, verbose_name="Poste des interlocuteurs")
    
    ordre_du_jour = models.TextField(blank=True, verbose_name="Ordre du jour")
    notes_preparation = models.TextField(blank=True, verbose_name="Notes de préparation")
    feedback = models.TextField(blank=True, verbose_name="Feedback")
    points_abordes = models.TextField(blank=True, verbose_name="Points abordés")
    questions_posées = models.TextField(blank=True, verbose_name="Questions posées")
    
    note_globale = models.PositiveIntegerField(null=True, blank=True, verbose_name="Note globale/10")
    points_positifs = models.TextField(blank=True, verbose_name="Points positifs")
    points_amelioration = models.TextField(blank=True, verbose_name="Points d'amélioration")
    suite_prevue = models.TextField(blank=True, verbose_name="Suite prévue")
    
    lieu = models.TextField(blank=True, verbose_name="Lieu de l'entretien")
    lien_video = models.URLField(blank=True, verbose_name="Lien visioconférence")
    codes_acces = models.TextField(blank=True, verbose_name="Codes d'accès")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)
    
    est_supprime = models.BooleanField(default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Entretien"
        verbose_name_plural = "Entretiens"
        ordering = ['-date_prevue']
    
    def __str__(self):
        return f"Entretien {self.get_type_entretien_display()} - {self.candidature}"
    
    def soft_delete(self):
        self.est_supprime = True
        self.save()

# ====================================================
# SYSTÈME D'ÉVALUATION (NOUVEAU)
# ====================================================
class EvaluationEntretien(models.Model):
    NOTE_CHOICES = [
        (1, '1 - Insuffisant'),
        (2, '2 - En développement'),
        (3, '3 - Satisfaisant'),
        (4, '4 - Bon'),
        (5, '5 - Excellent'),
    ]
    
    entretien = models.OneToOneField(Entretien, on_delete=models.CASCADE, related_name='evaluation')
    evaluateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Évaluateur (RH)")
    
    note_technique = models.PositiveIntegerField(choices=NOTE_CHOICES, verbose_name="Compétences techniques")
    note_communication = models.PositiveIntegerField(choices=NOTE_CHOICES, verbose_name="Communication")
    note_motivation = models.PositiveIntegerField(choices=NOTE_CHOICES, verbose_name="Motivation")
    note_culture = models.PositiveIntegerField(choices=NOTE_CHOICES, verbose_name="Fit culturel")
    
    points_forts = models.TextField(verbose_name="Points forts observés")
    points_amelioration = models.TextField(verbose_name="Points d'amélioration")
    recommandation = models.TextField(verbose_name="Recommandation")
    
    recommander = models.BooleanField(default=False, verbose_name="Recommander ce candidat")
    niveau_urgence = models.PositiveIntegerField(choices=[(1, 'Faible'), (2, 'Moyen'), (3, 'Élevé')], default=2, verbose_name="Niveau d'urgence")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Évaluation d'entretien"
        verbose_name_plural = "Évaluations d'entretien"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Évaluation de {self.entretien} par {self.evaluateur.get_full_name()}"
    
    @property
    def note_moyenne(self):
        notes = [self.note_technique, self.note_communication, self.note_motivation, self.note_culture]
        return sum(notes) / len(notes) if notes else 0