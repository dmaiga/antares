from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    ProfilCandidat, Diplome, ExperienceProfessionnelle,
    Document, Candidature, Adresse, Entretien
)
from authentication.models import User

@admin.register(Adresse)
class AdresseAdmin(admin.ModelAdmin):
    list_display = ('quartier', 'ville',  'pays', 'get_coordinates')
    list_filter = ('pays', 'ville')
    search_fields = ('quartier',  'ville', 'pays')
 
    
    def get_coordinates(self, obj):
        if obj.latitude and obj.longitude:
            return f"{obj.latitude:.6f}, {obj.longitude:.6f}"
        return "Non définies"
    get_coordinates.short_description = "Coordonnées"

@admin.register(ProfilCandidat)
class ProfilCandidatAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_email', 'get_phone', 'get_age', 
        'fourchette_salariale', 'recherche_active', 'derniere_connexion'
    )
    list_filter = (
        'genre', 'recherche_active', 'disponible', 
        
    )  # RETIRÉ 'pays' car il n'existe pas dans ProfilCandidat
    search_fields = (
        'user__first_name', 'user__last_name', 'user__email',
        'telephone', 'ville'
    )  # RETIRÉ 'pays' de search_fields
    readonly_fields = ('date_inscription', 'derniere_maj', 'derniere_connexion')
    ordering = ('-date_inscription',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': (
                'user', 'telephone', 'date_naissance', 'genre',
                'linkedin_url', 'portfolio_url'
            )
        }),
        ('Localisation', {
            'fields': ('adresse',)
        }),
        ('Préférences professionnelles', {
            'fields': (
                'salaire_min', 'salaire_max', 'recherche_active',
                'date_debut_recherche', 'disponible', 
                'rayon_mobilite'
            )
        }),
        ('Métadonnées', {
            'fields': (
                'accepte_newsletter', 'cgu_acceptees',
                'date_inscription', 'derniere_maj', 'derniere_connexion'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

    def get_phone(self, obj):
        return obj.telephone
    get_phone.short_description = 'Téléphone'

    def get_age(self, obj):
        if obj.date_naissance:
            from datetime import date
            today = date.today()
            age = today.year - obj.date_naissance.year - (
                (today.month, today.day) < (obj.date_naissance.month, obj.date_naissance.day)
            )
            return f"{age} ans"
        return "Non spécifié"
    get_age.short_description = 'Âge'

    def fourchette_salariale(self, obj):
        return obj.fourchette_salariale
    fourchette_salariale.short_description = 'Prétention salariale'

@admin.register(Diplome)
class DiplomeAdmin(admin.ModelAdmin):
    list_display = (
        'candidat', 'intitule', 'etablissement', 'niveau', 
        'domaine', 'date_obtention', 'mention', 'note'
    )
    list_filter = (
        'niveau', 'type_etablissement', 'pays_obtention', 
        'domaine'
    )
    search_fields = (
        'candidat__first_name', 'candidat__last_name', 
        'intitule', 'etablissement', 'domaine'
    )
    readonly_fields = ('duree_etudes',)
    ordering = ('-date_obtention',)
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'candidat', 'intitule', 'etablissement', 'type_etablissement'
            )
        }),
        ('Détails académiques', {
            'fields': (
                'niveau', 'domaine', 'date_debut', 'date_obtention',
                'mention', 'note'
            )
        }),
        ('Localisation', {
            'fields': ('pays_obtention', 'ville_obtention')
        }),
        ('Contenu', {
            'fields': ('description', 'competences_acquises')
        }),
        ('Calculé', {
            'fields': ('duree_etudes',),
            'classes': ('collapse',)
        }),
    )

    def duree_etudes(self, obj):
        if obj.duree_etudes:
            return f"{obj.duree_etudes} an(s)"
        return "Non calculable"
    duree_etudes.short_description = 'Durée des études'

@admin.register(ExperienceProfessionnelle)
class ExperienceProfessionnelleAdmin(admin.ModelAdmin):
    list_display = (
        'candidat', 'poste', 'entreprise', 'secteur', 
        'type_contrat', 'date_debut', 'date_fin', 'en_poste',
        'duree', 'remote'
    )
    list_filter = (
        'secteur', 'type_contrat', 'remote', 'pays',
        'en_poste'
    )
    search_fields = (
        'candidat__first_name', 'candidat__last_name',
        'poste', 'entreprise', 'lieu'
    )
    readonly_fields = ('duree',)
    ordering = ('-date_debut',)
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'candidat', 'poste', 'entreprise', 'secteur', 'type_contrat'
            )
        }),
        ('Localisation', {
            'fields': ('lieu', 'pays', 'remote')
        }),
        ('Période', {
            'fields': ('date_debut', 'date_fin', 'en_poste')
        }),
        ('Détails', {
            'fields': (
                'salaire', 'equipe', 'manager', 'contact_reference'
            )
        }),
        ('Contenu', {
            'fields': ('description', 'competences', 'realisation')
        }),
        ('Calculé', {
            'fields': ('duree',),
            'classes': ('collapse',)
        }),
    )

    def duree(self, obj):
        if obj.duree:
            return f"{obj.duree} mois"
        return "En cours"
    duree.short_description = 'Durée'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'candidat', 'nom', 'type_document', 'langue', 
        'version',  'est_actif', 
        'taille_formattee', 'date_upload'
    )
    list_filter = (
        'type_document', 'langue',  
        'est_actif', 'est_modele'
    )
    search_fields = (
        'candidat__first_name', 'candidat__last_name',
        'nom', 'mots_cles', 'description'
    )
    readonly_fields = ('taille_fichier', 'date_upload', 'date_maj', 'taille_formattee')
    ordering = ('-date_upload',)
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'candidat', 'nom', 'type_document', 'version'
            )
        }),
        ('Fichier', {
            'fields': ('fichier', 'taille_formattee')
        }),
        ('Métadonnées', {
            'fields': ('langue', 'description', 'mots_cles')
        }),
        ('Visibilité', {
            'fields': ( 'est_actif', 'est_modele')
        }),
        ('Dates', {
            'fields': ('date_upload', 'date_maj'),
            'classes': ('collapse',)
        }),
    )

    def taille_formattee(self, obj):
        return obj.taille_formattee
    taille_formattee.short_description = 'Taille'

@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = (
        'candidat', 'offre', 'statut', 'canal',
        'date_postulation', 'delai_reponse', 'nombre_relances'
    )
    list_filter = (
        'statut', 'canal', 'offre__societe', 'offre__type_offre'
    )
    search_fields = (
        'candidat__first_name', 'candidat__last_name',
        'offre__titre', 'offre__reference'
    )
    readonly_fields = ('date_postulation', 'date_mise_a_jour', 'delai_reponse')
    ordering = ('-date_postulation',)
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'candidat', 'offre', 'statut', 'canal'
            )
        }),
        ('Documents', {
            'fields': (
                'cv_utilise', 'lettre_motivation', 'documents_supplementaires'
            )
        }),
        ('Contenu', {
            'fields': ('motivation', 'points_forts', 'points_faibles', 'notes')
        }),
        ('Suivi', {
            'fields': ('nombre_relances', 'date_derniere_relance')
        }),
        ('Dates', {
            'fields': ('date_postulation', 'date_mise_a_jour', 'delai_reponse'),
            'classes': ('collapse',)
        }),
    )

    def delai_reponse(self, obj):
        if obj.delai_reponse:
            return f"{obj.delai_reponse} jours"
        return "En cours"
    delai_reponse.short_description = 'Délai de réponse'

@admin.register(Entretien)
class EntretienAdmin(admin.ModelAdmin):
    list_display = (
        'candidature', 'type_entretien', 'statut',
        'date_prevue', 'duree_prevue', 'note_globale'
    )
    list_filter = (
        'type_entretien', 'statut'
    )
    search_fields = (
        'candidature__candidat__first_name',
        'candidature__candidat__last_name',
        'candidature__offre__titre',
        'interlocuteurs'
    )
    readonly_fields = ('date_creation', 'date_maj')
    ordering = ('-date_prevue',)
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'candidature', 'type_entretien', 'statut'
            )
        }),
        ('Planning', {
            'fields': (
                'date_prevue', 'duree_prevue', 'date_reelle', 'duree_reelle'
            )
        }),
        ('Participants', {
            'fields': ('interlocuteurs', 'poste_interlocuteurs')
        }),
        ('Contenu', {
            'fields': (
                'ordre_du_jour', 'notes_preparation', 'points_abordes',
                'questions_posées', 'feedback'
            )
        }),
        ('Évaluation', {
            'fields': (
                'note_globale', 'points_positifs', 'points_amelioration',
                'suite_prevue'
            )
        }),
        ('Logistique', {
            'fields': ('lieu', 'lien_video', 'codes_acces'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_maj'),
            'classes': ('collapse',)
        }),
    )

# Correction du UserAdminCustom
class UserAdminCustom(UserAdmin):
    list_display = UserAdmin.list_display + ('role', 'date_joined', 'last_login')
    list_filter = UserAdmin.list_filter + ('role',)
    
    # CORRECTION : Utiliser 'email' au lieu de 'username' pour l'ordering
    ordering = ('email',)  # ou ('-date_joined',) selon votre préférence
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets = list(fieldsets)  # Convertir en liste pour modification
            # Ajouter la section relations candidat
            fieldsets.append(
                ('Relations Candidat', {
                    'fields': (),
                    'description': format_html(
                        """
                        <strong>Diplômes:</strong> {} |
                        <strong>Expériences:</strong> {} |
                        <strong>Documents:</strong> {} |
                        <strong>Candidatures:</strong> {}
                        """,
                        obj.diplomes.count(),
                        obj.experiences.count(),
                        obj.documents.count(),
                        obj.candidatures.count()
                    )
                })
            )
        return fieldsets

# Re-register User admin
if admin.site.is_registered(User):
    admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)