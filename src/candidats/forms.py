from django import forms
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django_summernote.widgets import SummernoteWidget
from django.utils import timezone
from django.conf import settings
from authentication.models import User
from .models import (
    ProfilCandidat, Diplome, ExperienceProfessionnelle,
    Document, Candidature, Adresse, Entretien, Competence,
    EvaluationEntretien ,
    STATUT_CANDIDATURE_CHOICES,CANAL_CANDIDATURE_CHOICES,NIVEAU_CHOICES 
)
from django.core.exceptions import ValidationError
from jobs.models import JobOffer,JobStatus,JobType
# ====================================================
# FORMULAIRES EXISTANTS MODIFIÉS
# ====================================================

class CompetenceForm(forms.ModelForm):
    class Meta:
        model = Competence
        fields = ['nom', 'categorie', 'niveau']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: , Anglais,Python, Communication, etc..'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'niveau': 'Niveau de maîtrise'
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class AdresseForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = ['quartier',  'ville', 'pays']  # AJOUT: code_postal
        widgets = {
            'quartier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quartier'
            }),
            'code_postal': forms.TextInput(attrs={  # NOUVEAU CHAMP
                'class': 'form-control',
                'placeholder': 'Code postal'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pays'
            })
        }

class DateInput(forms.DateInput):
    input_type = 'date'
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({'class': 'form-control'})
        super().__init__(*args, **kwargs)
    
    def format_value(self, value):
        if isinstance(value, str):
            return value
        if value:
            return value.strftime('%Y-%m-%d')
        return ''

class ProfilCandidatForm(forms.ModelForm):
    class Meta:
        model = ProfilCandidat
        fields = [
            'photo', 'telephone', 'telephone_second', 'date_naissance', 'genre', 'situation_familiale',
            'type_piece_identite', 'numero_piece_identite', 'date_delivrance_piece', 'lieu_delivrance_piece',
            'pretention_salariale', 'mission_temporaire', 'localite_souhaitee',
            'linkedin_url', 'facebook_url', 'instagram_url', 'portfolio_url',  
            'recherche_active', 'disponible',
            'accepte_newsletter', 'adresse'
        ]
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewImage(this)'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: +223 76 45 32 10',
                'help_text': 'Votre numéro principal de contact'
            }),
            'telephone_second': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: +223 70 12 34 56 (optionnel)',
                'help_text': 'Un numéro secondaire pour vous joindre'
            }),
            
            'date_naissance': DateInput(attrs={
                'placeholder': 'JJ/MM/AAAA',
                'help_text': 'Votre date de naissance'
            }),
            'genre': forms.Select(attrs={
                'class': 'form-select',
                'help_text': 'Civilité'
            }),
            'situation_familiale': forms.Select(attrs={
                'class': 'form-select',
                'help_text': 'Votre situation familiale'
            }),
            'type_piece_identite': forms.Select(attrs={  
                'class': 'form-select',
                'id': 'type_piece_identite',
                'help_text': 'Type de document d\'identité'
            }),
            'numero_piece_identite': forms.TextInput(attrs={ 
                'class': 'form-control',
                'placeholder': 'Ex: AB1234567',
                'id': 'numero_piece_identite',
                'help_text': 'Numéro de votre pièce d\'identité'
            }),
            'date_delivrance_piece': DateInput(attrs={
                'placeholder': 'JJ/MM/AAAA',
                'help_text': 'Date de délivrance du document'
            }),
            'lieu_delivrance_piece': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Bamako, Commune I',
                'help_text': 'Lieu où le document a été délivré'
            }),
            'pretention_salariale': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 150000',
                'step': '5',
                'help_text': 'Salaire Mensuel souhaité en FCFA'
            }),
            'localite_souhaitee': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Bamako, Sikasso, ou Télétravail',
                'help_text': 'Où souhaitez-vous travailler ?'
            }),
            
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/votrenom',
                'help_text': 'Lien vers votre profil LinkedIn'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://votreportfolio.com',
                'help_text': 'Lien vers votre portfolio en ligne'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/votrenom',
                'help_text': 'Lien vers votre profil Facebook (optionnel)'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/votrenom',
                'help_text': 'Lien vers votre profil Instagram (optionnel)'
            }),
       
            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Je suis disponible pour commencer rapidement'
            }),
            'recherche_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Je recherche activement un emploi'
            }),
            'accepte_newsletter': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Je souhaite recevoir des offres par email'
            }),
            'mission_temporaire': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'J\'accepte les missions temporaires'
            }),    
            'adresse': forms.Select(attrs={
                'class': 'form-select',
                'help_text': 'Votre adresse principale'
            }),
        }
        help_texts = {
            'disponible': "Cochez si vous êtes disponible pour commencer sous 15 jours",
            'recherche_active': "Cochez si vous recherchez activement un emploi",
            'mission_temporaire': "Cochez si vous acceptez les CDD, intérim ou missions",
            'accepte_newsletter': "Recevez nos meilleures offres par email",
        }
        labels = {
            'disponible': "Disponibilité immédiate",
            'recherche_active': "En recherche active",
            'mission_temporaire': "Missions temporaires acceptées",
            'accepte_newsletter': "Newsletter des offres",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs de pièce d'identité optionnels
        self.fields['type_piece_identite'].required = False
        self.fields['numero_piece_identite'].required = False
        self.fields['date_delivrance_piece'].required = False
        self.fields['lieu_delivrance_piece'].required = False
        
        # Ajouter des textes d'aide supplémentaires
        self.fields['telephone'].help_text = "Format international : +223 XX XX XX XX"
        self.fields['pretention_salariale'].help_text = "Salaire annuel brut souhaité en FCFA"
        self.fields['localite_souhaitee'].help_text = "Ville, région ou 'Télétravail'"

    def clean(self):
        cleaned_data = super().clean()
        type_piece = cleaned_data.get('type_piece_identite')
        numero_piece = cleaned_data.get('numero_piece_identite')
        date_delivrance = cleaned_data.get('date_delivrance_piece')
        lieu_delivrance = cleaned_data.get('lieu_delivrance_piece')
        
        # Validation conditionnelle : seulement si l'utilisateur commence à remplir les infos pièce
        if type_piece or numero_piece:
            # Si un type est sélectionné mais pas de numéro
            if type_piece and not numero_piece:
                self.add_error('numero_piece_identite', 
                              "Veuillez saisir le numéro de votre pièce d'identité.")
            
            # Si un numéro est saisi mais pas de type
            if numero_piece and not type_piece:
                self.add_error('type_piece_identite', 
                              "Veuillez sélectionner le type de votre pièce d'identité.")
            
            # Si type et numéro sont renseignés, vérifier date et lieu
            if type_piece and numero_piece:
                if not date_delivrance:
                    self.add_error('date_delivrance_piece', 
                                  "Veuillez renseigner la date de délivrance.")
                if not lieu_delivrance:
                    self.add_error('lieu_delivrance_piece', 
                                  "Veuillez renseigner le lieu de délivrance.")

        return cleaned_data    

    
class DiplomeForm(forms.ModelForm):
    class Meta:
        model = Diplome
        exclude = ['candidat', 'est_supprime']  # EXCLURE: est_supprime
        widgets = {
            'intitule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Master en Informatique'
            }),
            'etablissement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Université Paris-Saclay'
            }),
            'type_etablissement': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'domaine': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Informatique, Marketing, Finance...'
            }),
            'pays_obtention': forms.TextInput(attrs={  # CHANGÉ: De Select à TextInput
                'class': 'form-control',
                'placeholder': 'Pays d\'obtention'
            }),
            'ville_obtention': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville de l\'établissement'
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_obtention': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'mention': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Très Bien, Assez Bien...'
            }),
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': 0,
                'max': 20,
                'placeholder': 'Note sur 20'
            }),
            'description': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline', 'clear']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['insert', ['link']],
                        ['view', ['codeview', 'help']],
                    ],
                    'height': 200,
                    'placeholder': 'Décrivez votre formation, les matières principales, les projets réalisés...'
                }
            }),
            'competences': forms.SelectMultiple(attrs={  # CHANGÉ: SummernoteWidget à SelectMultiple
                'class': 'form-select',
                'size': 5
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_obtention = cleaned_data.get('date_obtention')
        
        if date_debut and date_obtention and date_debut > date_obtention:
            raise forms.ValidationError(
                "La date de début ne peut pas être postérieure à la date d'obtention."
            )
        
        return cleaned_data


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = ExperienceProfessionnelle
        exclude = ['candidat', 'est_supprime']  # EXCLURE: est_supprime
        widgets = {
            'poste': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Développeur Full Stack'
            }),
            'entreprise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'entreprise'
            }),
            'secteur': forms.Select(attrs={'class': 'form-select'}),
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville, Pays'
            }),
            'pays': forms.TextInput(attrs={  # CHANGÉ: De Select à TextInput
                'class': 'form-control',
                'placeholder': 'Pays'
            }),
            'remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'en_poste': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'salaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '5',
                'placeholder': 'Salaire Mensuel brut'
            }),
            'equipe': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Nombre de personnes dans l\'équipe'
            }),
            'description': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['insert', ['link']],
                        ['view', ['codeview']],
                    ],
                    'height': 250,
                    'placeholder': 'Décrivez vos missions principales, responsabilités...'
                }
            }),
            'competences': forms.SelectMultiple(attrs={  # CHANGÉ: SummernoteWidget à SelectMultiple
                'class': 'form-select',
                'size': 5
            }),
            'realisation': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Réalisations concrètes, projets menés...'
                }
            }),
            'manager': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom et prénom du manager'
            }),
            'contact_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email ou téléphone de référence'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        en_poste = cleaned_data.get('en_poste')
        
        if not en_poste and not date_fin:
            raise forms.ValidationError(
                "Veuillez spécifier une date de fin ou cocher 'Actuellement en poste'."
            )
        
        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError(
                "La date de début ne peut pas être postérieure à la date de fin."
            )
        
        if date_fin and date_fin > timezone.now().date() and not en_poste:
            raise forms.ValidationError(
                "La date de fin ne peut pas être dans le futur si vous n'êtes plus en poste."
            )
        
        return cleaned_data



class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['type_document', 'nom', 'fichier', 'langue', 'description', 'mots_cles',  'est_actif']
        widgets = {
            'type_document': forms.Select(attrs={'class': 'form-select'}),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Indiquer le nom du document partage EX: Attestation de stage, CV etc ...'
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.odt,.jpg,.png,.jpeg'
            }),
            'langue': forms.Select(attrs={'class': 'form-select'}),
            'mots_cles': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Management, Leadership, Anglais,Informatique - Mots-clés séparés par des virgules'
            }),

            'description': forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Décrivez le contenu ou l’importance du document... EX : " Diplôme de Licence en Informatique obtenu en 2022 ", " CV mis à jour avec 5 ans d’expérience en finance " )'
            }),

            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fichier'].validators = [
            FileExtensionValidator(allowed_extensions=[
                'pdf', 'doc', 'docx', 'odt', 'jpg', 'png', 'jpeg'
            ])
        ]


class SuiviCandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['statut', 'notes', 'points_forts', 'points_faibles']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points_forts': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points_faibles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les choix de statut selon l'état actuel
        statut_actuel = self.instance.statut if self.instance else None
        statuts_possibles = self.get_statuts_possibles(statut_actuel)
        self.fields['statut'].choices = statuts_possibles
        
        # Masquer le champ canal comme demandé
        if 'canal' in self.fields:
            self.fields['canal'].widget = forms.HiddenInput()
    
    def get_statuts_possibles(self, statut_actuel):
        # Définir les transitions de statut possibles
        transitions = {
            'POSTULE': [('POSTULE', 'Postulé'), ('RELANCE', 'Relancé'), ('RETIRE', 'Retiré')],
            'RELANCE': [('RELANCE', 'Relancé'), ('ENTRETIEN', 'Entretien'), ('REFUSE', 'Refusé')],
            'ENTRETIEN': [('ENTRETIEN', 'Entretien'), ('OFFRE', 'Offre reçue'), ('REFUSE', 'Refusé')],
            'OFFRE': [('OFFRE', 'Offre reçue'), ('ACCEPTE', 'Accepté'), ('REFUSE', 'Refusé')],
            'ACCEPTE': [('ACCEPTE', 'Accepté')],
            'REFUSE': [('REFUSE', 'Refusé')],
            'RETIRE': [('RETIRE', 'Retiré')],
        }
        return transitions.get(statut_actuel, STATUT_CANDIDATURE_CHOICES)
    

class EntretienForm(forms.ModelForm):
    class Meta:
        model = Entretien
        exclude = ['candidature', 'statut', 'date_reelle', 'duree_reelle', 'est_supprime']  # EXCLURE: est_supprime
        widgets = {
            'type_entretien': forms.Select(attrs={'class': 'form-select'}),
            'date_prevue': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'duree_prevue': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'step': 5,
                'placeholder': 'Durée en minutes'
            }),
            'interlocuteurs': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Noms des interlocuteurs'
            }),
            'poste_interlocuteurs': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postes des interlocuteurs'
            }),
            'ordre_du_jour': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points qui seront abordés pendant l\'entretien...'
                }
            }),
            'notes_preparation': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic']],
                        ['para', ['ul']],
                    ],
                    'height': 200,
                    'placeholder': 'Notes pour vous préparer à l\'entretien...'
                }
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse ou lieu de l\'entretien'
            }),
            'lien_video': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/xxx-yyyy-zzz'
            }),
            'codes_acces': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code d\'accès ou mot de passe'
            }),
        }
    
    def clean_date_prevue(self):
        date_prevue = self.cleaned_data.get('date_prevue')
        if date_prevue and date_prevue < timezone.now():
            raise forms.ValidationError("La date de l'entretien ne peut pas être dans le passé.")
        return date_prevue


class EntretienFeedbackForm(forms.ModelForm):
    class Meta:
        model = Entretien
        fields = ['feedback', 'points_abordes', 'questions_posees', 
                 'note_globale', 'points_positifs', 'points_amelioration', 'suite_prevue']
        widgets = {
            'feedback': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic']],
                        ['para', ['ul', 'ol']],
                    ],
                    'height': 200,
                    'placeholder': 'Feedback général sur l\'entretien...'
                }
            }),
            'points_abordes': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points abordés pendant l\'entretien...'
                }
            }),
            'questions_posees': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Questions posées et réponses...'
                }
            }),
            'note_globale': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10,
                'step': 0.5,
                'placeholder': 'Note sur 10'
            }),
            'points_positifs': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points positifs de l\'entretien...'
                }
            }),
            'points_amelioration': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points à améliorer pour les prochains entretiens...'
                }
            }),
            'suite_prevue': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 100,
                    'placeholder': 'Prochaines étapes prévues...'
                }
            }),
        }

# ====================================================
# NOUVEAU FORMULAIRE - ÉVALUATION ENTRETIEN
# ====================================================

class EvaluationEntretienForm(forms.ModelForm):
    class Meta:
        model = EvaluationEntretien
        fields = [
            'note_technique', 'note_communication', 'note_motivation', 'note_culture',
            'points_forts', 'points_amelioration', 'recommandation',
            'recommander', 'niveau_urgence'
        ]
        widgets = {
            'note_technique': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Compétences techniques'
            }),
            'note_communication': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Communication'
            }),
            'note_motivation': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Motivation'
            }),
            'note_culture': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Fit culturel'
            }),
            'points_forts': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points forts observés pendant l\'entretien...'
                }
            }),
            'points_amelioration': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points d\'amélioration pour le candidat...'
                }
            }),
            'recommandation': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic']],
                        ['para', ['ul', 'ol']],
                    ],
                    'height': 200,
                    'placeholder': 'Recommandation et avis global...'
                }
            }),
            'recommander': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'niveau_urgence': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les labels
        self.fields['note_technique'].label = "Compétences Techniques"
        self.fields['note_communication'].label = "Communication"
        self.fields['note_motivation'].label = "Motivation"
        self.fields['note_culture'].label = "Fit Culturel"
        self.fields['points_forts'].label = "Points Forts Observés"
        self.fields['points_amelioration'].label = "Points d'Amélioration"
        self.fields['recommandation'].label = "Recommandation"
        self.fields['recommander'].label = "Recommander ce candidat"
        self.fields['niveau_urgence'].label = "Niveau d'Urgence"

# ====================================================
# FORMULAIRES DE SUPPRESSION (SOFT DELETE)
# ====================================================

class SoftDeleteForm(forms.Form):
    """
    Formulaire générique pour la suppression logique
    """
    confirmation = forms.BooleanField(
        required=True,
        label="Je confirme la suppression",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    raison = forms.CharField(
        required=False,
        label="Raison de la suppression (optionnel)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Pourquoi souhaitez-vous supprimer cet élément ?'
        })
    )

class SuiviCandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['statut', 'notes', 'points_forts', 'points_faibles']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points_forts': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points_faibles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les choix de statut selon l'état actuel
        statut_actuel = self.instance.statut if self.instance else None
        statuts_possibles = self.get_statuts_possibles(statut_actuel)
        self.fields['statut'].choices = statuts_possibles
        
        # Masquer le champ canal comme demandé
        if 'canal' in self.fields:
            self.fields['canal'].widget = forms.HiddenInput()
    
    def get_statuts_possibles(self, statut_actuel):
        # Définir les transitions de statut possibles avec vos choix réels
        transitions = {
            'POSTULE': [('POSTULE', 'Postulé'), ('RELANCE', 'Relancé'), ('RETIRE', 'Retiré')],
            'RELANCE': [('RELANCE', 'Relancé'), ('ENTRETIEN', 'Entretien'), ('REFUSE', 'Refusé')],
            'ENTRETIEN': [('ENTRETIEN', 'Entretien'), ('OFFRE', 'Offre reçue'), ('REFUSE', 'Refusé')],
            'OFFRE': [('OFFRE', 'Offre reçue'), ('ACCEPTE', 'Accepté'), ('REFUSE', 'Refusé')],
            'ACCEPTE': [('ACCEPTE', 'Accepté')],
            'REFUSE': [('REFUSE', 'Refusé')],
            'RETIRE': [('RETIRE', 'Retiré')],
        }
        return transitions.get(statut_actuel, STATUT_CANDIDATURE_CHOICES)

# candidats/forms.py
from django import forms
from django_summernote.widgets import SummernoteWidget
from django.core.exceptions import ValidationError
from .models import Candidature, Document

class CandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['offre', 'cv_utilise', 'motivation', 'points_forts']
        widgets = {
            'offre': forms.HiddenInput(),
            'cv_utilise': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'motivation': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic']],
                        ['para', ['ul', 'ol']],
                        ['view', ['codeview']],
                    ],
                    'height': 150,
                    'placeholder': 'Expliquez brièvement pourquoi vous êtes intéressé par ce poste... '
                }
            }),
            'points_forts': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Quelles sont vos compétences et qualités les plus pertinentes pour ce poste? '
            }),
        }
        labels = {
            'cv_utilise': 'CV *',
            'motivation': 'Motivation',
            'points_forts': 'Points forts pour ce poste'
        }
        help_texts = {
            'points_forts': 'Mettez en avant vos compétences et qualités les plus pertinentes pour ce poste spécifique',
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user:
            self.user = user
            # Documents CV actifs
            cvs = user.documents.filter(
                type_document='CV', 
                est_actif=True, 
                est_supprime=False
            )
            self.fields['cv_utilise'].queryset = cvs
            
            # Vérifier le profil du candidat
            self.profil_complet = self.verifier_profil_identite(user)
            
            # Vérifier les documents d'identité
            self.documents_identite = self.verifier_documents_identite(user)
            
            # Si l'utilisateur n'a pas de CV, afficher un message
            if not cvs.exists():
                self.fields['cv_utilise'].help_text = """
                <div class="alert alert-warning mt-2">
                    <i class="fas fa-exclamation-triangle"></i>
                    Vous n'avez aucun CV actif. 
                    <a href="/antares/candidat/documents/ajouter/" class="alert-link">
                        Créer un CV
                    </a> avant de postuler.
                </div>
                """
    
    def verifier_profil_identite(self, user):
        """Vérifie si le profil contient les informations de pièce d'identité"""
        try:
            profil = user.profil_candidat
            return bool(profil.type_piece_identite and profil.numero_piece_identite)
        except ProfilCandidat.DoesNotExist:
            return False
    
    def verifier_documents_identite(self, user):
        """Vérifie si l'utilisateur a des documents d'identité uploadés"""
        return user.documents.filter(
            type_document='PIECE_IDENTITE',
            est_actif=True,
            est_supprime=False
        ).exists()
    
    def is_ready_to_submit(self):
        """Vérifie si le formulaire peut être soumis"""
        return self.profil_complet and self.fields['cv_utilise'].queryset.exists()
    
    def get_tooltip_message(self):
        """Message d'info-bulle selon l'état"""
        if not self.profil_complet:
            return "Complétez votre profil pour postuler"
        elif not self.fields['cv_utilise'].queryset.exists():
            return "Ajoutez un CV pour postuler"
        return "Prêt à postuler"
    
    def clean(self):
        cleaned_data = super().clean()
        cv_utilise = cleaned_data.get('cv_utilise')
        
        # Validation : au moins un CV doit être sélectionné
        if not cv_utilise:
            raise ValidationError({
                'cv_utilise': 'Vous devez sélectionner un CV pour postuler.'
            })
        
        # Validation : profil complet avec pièce d'identité
        if not self.profil_complet:
            raise ValidationError(
                "Veuillez compléter les informations de votre pièce d'identité dans votre profil avant de postuler."
            )
        
        return cleaned_data
    
    def get_alertes(self):
        """Retourne les alertes à afficher à l'utilisateur"""
        alertes = []
        
        if not self.profil_complet:
            alertes.append({
                'niveau': 'danger',
                'message': f"""
                <i class="fas fa-id-card me-2"></i>
                <strong>Information requise :</strong> Pour pouvoir postuler, il faudrait avoir au moins un CV et avoir rempli 
                dans votre profil les informations relatives à votre pièce d'identité.
                <a href="/antares/candidat/profil/" class="alert-link">Complétez votre profil</a>.
                """,
                'obligatoire': True
            })
        
        if not self.documents_identite:
            alertes.append({
                'niveau': 'warning',
                'message': f"""
                <i class="fas fa-file-upload me-2"></i>
                <strong>Conseil :</strong> Renseignez vos expériences professionnelles et compétences dans la plateforme 
                pour mettre en avant que vous êtes le candidat idéal pour le poste.
                <a href="/antares/candidat/documents/ajouter/" class="alert-link">Ajouter des documents</a>.
                """,
                'obligatoire': False
            })
        
        
        return alertes
    




# ====================================================
# FORMULAIRES SPECIFIQUES AU BACKOFFICE (RH/RECRUTEUR)
# ====================================================

from django import forms
from django.db.models import Q
from django_summernote.widgets import SummernoteWidget


class CandidatFilterForm(forms.Form):
    """
    Formulaire de filtrage avancé pour la liste des candidats (Vue 360)
    """
    q = forms.CharField(
        required=False,
        label="Recherche globale",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom, prénom, email, téléphone, compétence, localité...'
        })
    )
    
    competence = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Competence.objects.filter(est_supprime=False),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'data-placeholder': 'Filtrer par compétence...'
        }),
        label="Compétences"
    )
    
    source_competence = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Toutes sources'),
            ('profil', 'Profil uniquement'),
            ('diplomes', 'Diplômes uniquement'),
            ('experiences', 'Expériences uniquement')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Source des compétences"
    )

    niveau_etude = forms.ChoiceField(
        required=False,
        choices=[('', '---------')] + NIVEAU_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Niveau d'étude minimum"
    )
    
    localite = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ville ou pays souhaité'
        }),
        label="Localisation"
    )
    
    statut_candidature = forms.ChoiceField(
        required=False,
        choices=[('', '---------')] + STATUT_CANDIDATURE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Statut de candidature actif"
    )
    
    recherche_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="En recherche active seulement"
    )
    
    disponible = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Disponible immédiatement seulement"
    )
    type_offre = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les types')] + list(JobType.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Type d'offre"
    )

    offre = forms.ModelChoiceField(
        required=False,
        queryset=JobOffer.objects.none(),  # vide par défaut
        empty_label="Toutes les offres",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    statut = forms.ChoiceField(  # Modifié: ChoiceField au lieu de MultipleChoiceField
        required=False,
        choices=[('', 'Tous les statuts')] + STATUT_CANDIDATURE_CHOICES,  # Ajout option "Tous"
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Statut"
    )
    
    date_min = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Postulé après le"
    )
    
    date_max = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Postulé avant le"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Charger dynamiquement les offres
        self.fields['offre'].queryset = JobOffer.objects.all()

class CandidatureBackofficeForm(forms.ModelForm):
    """
    Formulaire COMPLET de gestion d'une candidature pour le backoffice.
    Permet de changer le statut, noter, etc.
    """
    class Meta:
        model = Candidature
        fields = [
            'statut', 'notes', 'motivation', 'points_forts', 'points_faibles'
        ]
        widgets = {
            'statut': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline']],
                        ['para', ['ul', 'ol']],
                        ['view', ['codeview']],
                    ],
                    'height': 150,
                    'placeholder': 'Notes internes pour le recruteur...'
                }
            }),
            'motivation': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic']],
                        ['para', ['ul', 'ol']],
                    ],
                    'height': 150,
                    'placeholder': 'Résumé de la motivation du candidat...'
                }
            }),
            'points_forts': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points forts du candidat pour ce poste...'
                }
            }),
            'points_faibles': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points faibles ou à améliorer...'
                }
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer le champ canal comme demandé
        if 'canal' in self.fields:
            self.fields['canal'].widget = forms.HiddenInput()
        
        # Réorganiser l'ordre des champs si nécessaire
        self.order_fields(['statut', 'motivation', 'points_forts', 'points_faibles', 'notes'])

class PlanifierEntretienForm(forms.ModelForm):
    """
    Formulaire pour planifier un nouvel entretien (ModelForm)
    """
    class Meta:
        model = Entretien
        fields = ['candidature', 'type_entretien', 'date_prevue', 'duree_prevue', 
                 'interlocuteurs', 'notes_preparation', 'lieu', 'lien_video']
        widgets = {
            'candidature': forms.HiddenInput(),
            'type_entretien': forms.Select(attrs={'class': 'form-select'}),
            'date_prevue': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duree_prevue': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'placeholder': 'Durée en minutes'
            }),
            'interlocuteurs': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Noms des interlocuteurs'
            }),
            'notes_preparation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Grille de candidature, questions à poser, points à valider...'
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse ou lieu de l\'entretien'
            }),
            'lien_video': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/xxx-yyyy-zzz'
            }),
        }
        labels = {
            'date_prevue': "Date et heure de l'entretien",
            'duree_prevue': "Durée prévue (minutes)",
            'notes_preparation': "Notes de préparation",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les candidatures valides
        self.fields['candidature'].queryset = Candidature.objects.filter(
            est_supprime=False
        ).select_related('candidat', 'offre')
    
    def clean_date_prevue(self):
        date_prevue = self.cleaned_data.get('date_prevue')
        if date_prevue and date_prevue < timezone.now():
            raise forms.ValidationError("La date de l'entretien ne peut pas être dans le passé.")
        return date_prevue
    

    

class EntretienCompteRenduForm(forms.ModelForm):
    """
    Formulaire complet pour saisir le compte-rendu détaillé après un entretien.
    Utilise Summernote pour une mise en forme riche.
    """
    class Meta:
        model = Entretien
        fields = [
            'statut', 'date_reelle', 'duree_reelle',
            'feedback', 'points_abordes', 'questions_posees',
            'note_globale', 'points_positifs', 'points_amelioration', 'suite_prevue'
        ]
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'date_reelle': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duree_reelle': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Durée réelle en minutes'
            }),
            'feedback': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['insert', ['link']],
                        ['view', ['codeview', 'help']],
                    ],
                    'height': 250,
                    'placeholder': 'Feedback général et impression sur l\'entretien...'
                }
            }),
            'points_abordes': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul', 'ol']],
                    ],
                    'height': 200,
                    'placeholder': 'Liste des sujets et points techniques abordés...'
                }
            }),
            'questions_posees': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul', 'ol']],
                    ],
                    'height': 200,
                    'placeholder': 'Questions posées par le candidat et réponses apportées...'
                }
            }),
            'note_globale': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10,
                'step': 0.5,
                'placeholder': 'Note sur 10'
            }),
            'points_positifs': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points forts, compétences confirmées, atouts du candidat...'
                }
            }),
            'points_amelioration': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 150,
                    'placeholder': 'Points faibles, lacunes, axes d\'amélioration pour le candidat...'
                }
            }),
            'suite_prevue': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold']],
                        ['para', ['ul']],
                    ],
                    'height': 100,
                    'placeholder': 'Prochaines étapes : autre entretien, test, délai de réponse...'
                }
            }),
        }

class EvaluationEntretienForm(forms.ModelForm):
    class Meta:
        model = EvaluationEntretien
        fields = [
            'note_technique', 'commentaire_technique',
            'note_communication', 'commentaire_communication',
            'note_motivation', 'commentaire_motivation',
            'note_culture', 'commentaire_culture',
            'points_forts', 'points_amelioration',
            'recommandation', 'recommander', 'niveau_urgence'
        ]
        widgets = {
            'commentaire_technique': forms.Textarea(attrs={'class': 'summernote'}),
            'commentaire_communication': forms.Textarea(attrs={'class': 'summernote'}),
            'commentaire_motivation': forms.Textarea(attrs={'class': 'summernote'}),
            'commentaire_culture': forms.Textarea(attrs={'class': 'summernote'}),
            'points_forts': forms.Textarea(attrs={'class': 'summernote'}),
            'points_amelioration': forms.Textarea(attrs={'class': 'summernote'}),
            'recommandation': forms.Textarea(attrs={'class': 'summernote'}),
        }


  

class CandidatureFilterForm(forms.Form):
    """
    
    Formulaire pour filtrer les candidatures par offre, statut, etc.
    """
    offre = forms.ModelChoiceField(
        required=False,
        queryset=JobOffer.objects.filter(statut='OUVERT', visible_sur_site=True),
        empty_label="Toutes les offres",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    statut = forms.MultipleChoiceField(
        required=False,
        choices=STATUT_CANDIDATURE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label="Statut(s)"
    )
    
    canal = forms.MultipleChoiceField(
        required=False,
        choices=CANAL_CANDIDATURE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label="Canal(s) de recrutement"
    )
    
    date_min = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Postulé après le"
    )
    
    date_max = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Postulé avant le"
    )

class NoteInterneForm(forms.Form):
    """
    Formulaire rapide pour ajouter une note interne à une candidature.
    """
    note = forms.CharField(
        widget=SummernoteWidget(attrs={
            'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic']],
                    ['para', ['ul', 'ol']],
                ],
                'height': 200,
                'placeholder': 'Ajoutez une note interne...'
            }
        })
    )
    is_important = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Marquer comme importante",
        help_text="Les notes importantes sont mises en évidence."
    )


# forms.py
#from django import forms
#
#
#class CandidatureSpontaneeForm(forms.ModelForm):
#    class Meta:
#        model = CandidatureSpontanee
#        fields = [
#            'prenom', 'nom', 'email', 'telephone', 
#            'poste_recherche', 'domaine_expertise', 'annees_experience',
#            'niveau_etude', 'competences', 'cv', 'lettre_motivation',
#            'source_recrutement', 'disponibilite', 'pretentions_salariales',
#            'message_complementaire'
#        ]
#        widgets = {
#            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
#            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
#            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
#            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+XXX XX XX XX XX'}),
#            'poste_recherche': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Développeur Python'}),
#            'domaine_expertise': forms.Select(attrs={'class': 'form-select'}),
#            'annees_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
#            'niveau_etude': forms.Select(attrs={'class': 'form-select'}),
#            'competences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, Django, React, ...'}),
#            'cv': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
#            'lettre_motivation': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
#            'source_recrutement': forms.Select(attrs={'class': 'form-select'}),
#            'disponibilite': forms.Select(attrs={'class': 'form-select'}),
#            'pretentions_salariales': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 40-45K€'}),
#            'message_complementaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Votre message...'}),
#        }
#    
#    def clean_cv(self):
#        cv = self.cleaned_data.get('cv')
#        if cv:
#            if cv.size > 5 * 1024 * 1024:  # 5MB max
#                raise forms.ValidationError("Le fichier CV ne doit pas dépasser 5MB.")
#            if not cv.name.lower().endswith(('.pdf', '.doc', '.docx')):
#                raise forms.ValidationError("Format de fichier non supporté. Utilisez PDF, DOC ou DOCX.")
#        return cv