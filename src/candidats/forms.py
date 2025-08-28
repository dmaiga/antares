from django import forms
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django_summernote.widgets import SummernoteWidget
from django.utils import timezone
from django.conf import settings
from authentication.models import User
from .models import (
    ProfilCandidat, Diplome, ExperienceProfessionnelle,
    Document, Candidature, Adresse, Entretien, Competence,
    EvaluationEntretien  # NOUVEAU MODÈLE
)

# ====================================================
# FORMULAIRES EXISTANTS MODIFIÉS
# ====================================================

class CompetenceForm(forms.ModelForm):
    class Meta:
        model = Competence
        fields = ['nom', 'categorie', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Python, Communication, Anglais, etc..'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez la compétence'
            }),
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
        fields = ['ligne1', 'code_postal', 'ville', 'pays']  # AJOUT: code_postal
        widgets = {
            'ligne1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro et rue'
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


class ProfilCandidatForm(forms.ModelForm):
    class Meta:
        model = ProfilCandidat
        fields = [
            'photo', 'telephone', 'date_naissance', 'genre',
            'salaire_min', 'salaire_max',
            'disponible', 'mobilite_geographique', 'rayon_mobilite',
            'linkedin_url', 'portfolio_url',
            'recherche_active', 'date_debut_recherche',
            'accepte_newsletter', 'competences', 'adresse'
        ]
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+223 XXXXXXXX'
            }),
            'date_naissance': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'salaire_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Salaire minimum annuel',
                'step': '1000'
            }),
            'salaire_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Salaire maximum annuel',
                'step': '1000'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/votrenom'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://votreportfolio.com'
            }),
            'date_debut_recherche': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'rayon_mobilite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 10
            }),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mobilite_geographique': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recherche_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accepte_newsletter': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'competences': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'adresse': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        salaire_min = cleaned_data.get('salaire_min')
        salaire_max = cleaned_data.get('salaire_max')

        if salaire_min and salaire_max and salaire_min > salaire_max:
            raise forms.ValidationError(
                "Le salaire minimum ne peut pas être supérieur au salaire maximum."
            )
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
                'step': '1000',
                'placeholder': 'Salaire annuel brut'
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
        fields = ['type_document', 'nom', 'fichier', 'langue', 'description', 'mots_cles', 'est_public', 'est_actif']
        widgets = {
            'type_document': forms.Select(attrs={'class': 'form-select'}),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CV Développeur FullStack, Lettre Motivation Apple...'
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.odt,.jpg,.png,.jpeg'
            }),
            'langue': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du document...'
            }),
            'mots_cles': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: python, django, react, gestion-projet'
            }),
            'est_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fichier'].validators = [
            FileExtensionValidator(allowed_extensions=[
                'pdf', 'doc', 'docx', 'odt', 'jpg', 'png', 'jpeg'
            ])
        ]


class CandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['offre', 'cv_utilise', 'lettre_motivation', 'canal', 'motivation', 'documents_supplementaires']
        widgets = {
            'offre': forms.HiddenInput(),
            'cv_utilise': forms.Select(attrs={'class': 'form-select'}),
            'lettre_motivation': forms.Select(attrs={'class': 'form-select'}),
            'canal': forms.Select(attrs={'class': 'form-select'}),
            'motivation': SummernoteWidget(attrs={
                'summernote': {
                    'toolbar': [
                        ['style', ['bold', 'italic']],
                        ['para', ['ul', 'ol']],
                        ['view', ['codeview']],
                    ],
                    'height': 200,
                    'placeholder': 'Expliquez pourquoi vous êtes intéressé par ce poste ...'
                }
            }),
            'documents_supplementaires': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Filtrage des documents par type et statut actif
            self.fields['cv_utilise'].queryset = user.documents.filter(
                type_document='CV', est_actif=True, est_supprime=False  # AJOUT: est_supprime
            )
            self.fields['lettre_motivation'].queryset = user.documents.filter(
                type_document='LM', est_actif=True, est_supprime=False  # AJOUT: est_supprime
            )
            self.fields['documents_supplementaires'].queryset = user.documents.filter(
                type_document__in=['DIPLOME', 'RECOMMANDATION', 'PORTFOLIO', 'CERTIFICAT'],
                est_actif=True, est_supprime=False  # AJOUT: est_supprime
            )


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
                'min': 15,
                'step': 15,
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
        fields = ['feedback', 'points_abordes', 'questions_posées', 
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
            'questions_posées': SummernoteWidget(attrs={
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