from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Exists, OuterRef
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from authentication.models import User
from jobs.models import JobOffer,JobStatus
from .models import (
    ProfilCandidat, Diplome, ExperienceProfessionnelle,
    Document, Candidature, Adresse, Entretien, Competence,
    STATUT_CANDIDATURE_CHOICES,STATUT_ENTRETIEN_CHOICES,
    EvaluationEntretien  # NOUVEAU MODÈLE
)
from notes.models import NoteInterne,NoteReception

from .forms import (
    ProfilCandidatForm, DiplomeForm, ExperienceForm,
    DocumentForm, CandidatureForm, AdresseForm,
    UserUpdateForm, CompetenceForm, EntretienForm,
    EntretienFeedbackForm, EvaluationEntretienForm,  # NOUVEAUX FORMULAIRES
    SoftDeleteForm  # NOUVEAU FORMULAIRE
)
from django.db.models import Case, When, IntegerField, BooleanField, Exists, OuterRef
from django.db.models import Q, Avg, Sum, Count, Min, Max  
from django.utils import timezone
from django.utils.timezone import datetime
from datetime import timedelta
from django.http import JsonResponse

def check_candidat(user):
    """Vérifie si l'utilisateur est un candidat"""
    return user.role == 'candidat'

def get_candidat_profile(user):
    """Récupère ou crée le profil candidat"""
    profil, created = ProfilCandidat.objects.get_or_create(user=user)
    return profil

# Tableau de bord
@login_required
def dashboard(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    profil = get_candidat_profile(request.user)
    today = timezone.now().date()

    candidature_exists = Candidature.objects.filter(
        candidat=request.user,
        offre=OuterRef('pk')
    )

    # Offres ouvertes
    offres_ouvertes = JobOffer.objects.filter(
        statut=JobStatus.OUVERT,
        visible_sur_site=True
    ).annotate(
        deja_postule=Exists(candidature_exists)
    ).order_by('-date_publication')[:6]

    # Si moins de 6 → compléter avec expirées
    if offres_ouvertes.count() < 6:
        nb_restant = 6 - offres_ouvertes.count()
        offres_expires = JobOffer.objects.filter(
            statut=JobStatus.EXPIRE,
            visible_sur_site=True
        ).annotate(
            deja_postule=Exists(candidature_exists)
        ).order_by('-date_publication')[:nb_restant]

        offres_recentes = list(offres_ouvertes) + list(offres_expires)
    else:
        offres_recentes = offres_ouvertes

    # Ajouter la propriété est_expiree à chaque offre
    for offre in offres_recentes:
        offre.est_expiree_db = offre.statut == JobStatus.EXPIRE or (offre.date_limite and offre.date_limite < today)

    context = {
        'profil': profil,
        'diplomes': request.user.diplomes.filter(est_supprime=False),
        'experiences': request.user.experiences.filter(est_supprime=False).order_by('-date_debut'),
        'documents_recents': request.user.documents.filter(est_supprime=False).order_by('-date_upload')[:5],
        'documents': request.user.documents.filter(est_supprime=False),
        'candidatures': request.user.candidatures.filter(est_supprime=False).select_related('offre'),
        'offres_recentes': offres_recentes,
        'today': today
    }
    return render(request, 'candidats/client/dashboard.html', context)

# Changement de mot de passe
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'candidats/client/password_change.html'
    success_url = reverse_lazy('dashboard_candidat')

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été changé avec succès.")
        return super().form_valid(form)

# Profil
@login_required
def edit_profil(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    user = request.user
    profil = get_candidat_profile(user)
    adresse = profil.adresse if profil.adresse else None

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profil_form = ProfilCandidatForm(request.POST, request.FILES, instance=profil)
        adresse_form = AdresseForm(request.POST, instance=adresse)

        if user_form.is_valid() and profil_form.is_valid() and adresse_form.is_valid():
            user_form.save()
            adresse = adresse_form.save()
            profil = profil_form.save(commit=False)
            profil.adresse = adresse
            profil.save()
            profil_form.save_m2m()
            messages.success(request, "Profil mis à jour avec succès")
            return redirect('dashboard_candidat')
    else:
        user_form = UserUpdateForm(instance=user)
        profil_form = ProfilCandidatForm(instance=profil)
        adresse_form = AdresseForm(instance=adresse)

    return render(request, 'candidats/client/edit_profil.html', {
        'user_form': user_form,
        'profil_form': profil_form,
        'adresse_form': adresse_form
    })

# Diplômes
@login_required
def diplome_list(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    diplomes = request.user.diplomes.filter(est_supprime=False)
    return render(request, 'candidats/client/diplome/diplome_list.html', {'diplomes': diplomes})

@login_required
def diplome_create(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    if request.method == 'POST':
        form = DiplomeForm(request.POST)
        if form.is_valid():
            diplome = form.save(commit=False)
            diplome.candidat = request.user
            diplome.save()
            form.save_m2m()  # Pour les compétences
            messages.success(request, "Diplôme ajouté avec succès")
            return redirect('diplome_list')
    else:
        form = DiplomeForm()
    
    return render(request, 'candidats/client/diplome/diplome_form.html', {'form': form})

@login_required
def diplome_update(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    diplome = get_object_or_404(Diplome, pk=pk, candidat=request.user, est_supprime=False)
    
    if request.method == 'POST':
        form = DiplomeForm(request.POST, instance=diplome)
        if form.is_valid():
            form.save()
            messages.success(request, "Diplôme mis à jour avec succès")
            return redirect('diplome_list')
    else:
        form = DiplomeForm(instance=diplome)
    
    return render(request, 'candidats/client/diplome/diplome_form.html', {'form': form})

@login_required
def diplome_soft_delete(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    diplome = get_object_or_404(Diplome, pk=pk, candidat=request.user, est_supprime=False)
    
    if request.method == 'POST':
        form = SoftDeleteForm(request.POST)
        if form.is_valid():
            diplome.soft_delete()
            messages.success(request, "Diplôme supprimé avec succès")
            return redirect('diplome_list')
    else:
        form = SoftDeleteForm()
    
    return render(request, 'candidats/client/diplome/diplome_confirm_delete.html', {
        'diplome': diplome,
        'form': form
    })

# Expériences (mêmes modifications que pour les diplômes)
@login_required
def experience_list(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    experiences = request.user.experiences.filter(est_supprime=False).order_by('-date_debut')
    return render(request, 'candidats/client/experience/experience_list.html', {'experiences': experiences})

@login_required
def experience_create(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.candidat = request.user
            experience.save()
            form.save_m2m()  # Pour les compétences
            messages.success(request, "Expérience ajoutée avec succès")
            return redirect('experience_list')
    else:
        form = ExperienceForm()
    
    return render(request, 'candidats/client/experience/experience_form.html', {'form': form})

@login_required
def experience_update(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    experience = get_object_or_404(ExperienceProfessionnelle, pk=pk, candidat=request.user, est_supprime=False)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, "Expérience mise à jour avec succès")
            return redirect('experience_list')
    else:
        form = ExperienceForm(instance=experience)
    
    return render(request, 'candidats/client/experience/experience_form.html', {'form': form})

@login_required
def experience_soft_delete(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    experience = get_object_or_404(ExperienceProfessionnelle, pk=pk, candidat=request.user, est_supprime=False)
    
    if request.method == 'POST':
        form = SoftDeleteForm(request.POST)
        if form.is_valid():
            experience.soft_delete()
            messages.success(request, "Expérience supprimée avec succès")
            return redirect('experience_list')
    else:
        form = SoftDeleteForm()
    
    return render(request, 'candidats/client/experience/experience_confirm_delete.html', {
        'experience': experience,
        'form': form
    })

# Compétences
@login_required
def competence_list(request):
    competences = Competence.objects.filter(est_supprime=False)
    return render(request, 'candidats/client/competence/competence_list.html', {'competences': competences})

@login_required
def competence_create(request):
    if request.method == 'POST':
        form = CompetenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Compétence ajoutée avec succès")
            return redirect('competence_list')
    else:
        form = CompetenceForm()
    return render(request, 'candidats/client/competence/competence_form.html', {'form': form})

@login_required
def competence_update(request, pk):
    competence = get_object_or_404(Competence, pk=pk, est_supprime=False)
    if request.method == 'POST':
        form = CompetenceForm(request.POST, instance=competence)
        if form.is_valid():
            form.save()
            messages.success(request, "Compétence mise à jour avec succès")
            return redirect('competence_list')
    else:
        form = CompetenceForm(instance=competence)
    return render(request, 'candidats/client/competence/competence_form.html', {'form': form})

@login_required
def competence_soft_delete(request, pk):
    competence = get_object_or_404(Competence, pk=pk, est_supprime=False)
    if request.method == 'POST':
        form = SoftDeleteForm(request.POST)
        if form.is_valid():
            competence.soft_delete()
            messages.success(request, "Compétence supprimée avec succès")
            return redirect('competence_list')
    else:
        form = SoftDeleteForm()
    return render(request, 'candidats/client/competence/competence_confirm_delete.html', {
        'competence': competence,
        'form': form
    })

# Documents
@login_required
def document_list(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    documents = request.user.documents.filter(est_supprime=False)
    return render(request, 'candidats/client/document/document_list.html', {'documents': documents})

@login_required
def document_create(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.candidat = request.user
            document.save()
            messages.success(request, "Document ajouté avec succès")
            return redirect('document_list')
    else:
        form = DocumentForm()
    
    return render(request, 'candidats/client/document/document_form.html', {'form': form})

@login_required
def document_update(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    document = get_object_or_404(Document, pk=pk, candidat=request.user, est_supprime=False)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "Document mis à jour avec succès")
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)
    
    return render(request, 'candidats/client/document/document_form.html', {'form': form})

@login_required
def document_soft_delete(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    document = get_object_or_404(Document, pk=pk, candidat=request.user, est_supprime=False)
    
    if request.method == 'POST':
        form = SoftDeleteForm(request.POST)
        if form.is_valid():
            document.soft_delete()
            messages.success(request, "Document supprimé avec succès")
            return redirect('document_list')
    else:
        form = SoftDeleteForm()
    
    return render(request, 'candidats/client/document/document_confirm_delete.html', {
        'document': document,
        'form': form
    })

# Candidatures
@login_required
def candidature_list(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    candidatures = request.user.candidatures.filter(est_supprime=False).select_related('offre')
    return render(request, 'candidats/client/candidature/candidature_list.html', {'candidatures': candidatures})


@login_required
def candidature_detail(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    candidature = get_object_or_404(Candidature, pk=pk, candidat=request.user, est_supprime=False)
    entretiens = candidature.entretiens.filter(est_supprime=False)
    
    return render(request, 'candidats/client/candidature/candidature_detail.html', {
        'candidature': candidature,
        'entretiens': entretiens
    })

# candidats/views.py

@login_required
def apply_job(request, job_id):
    # Correction: utiliser visible_sur_site au lieu de est_active
    offre = get_object_or_404(JobOffer, pk=job_id, visible_sur_site=True)
    
    # Vérifier si l'utilisateur a déjà postulé
    deja_postule = Candidature.objects.filter(
        candidat=request.user, 
        offre=offre, 
        est_supprime=False
    ).exists()
    
    if deja_postule:
        messages.warning(request, "Vous avez déjà postulé à cette offre.")
        return redirect('job_detail', pk=job_id)
    
    if request.method == 'POST':
        form = CandidatureForm(request.POST, user=request.user)
        if form.is_valid():
            candidature = form.save(commit=False)
            candidature.candidat = request.user
            candidature.offre = offre
            candidature.save()
            
            # Sauvegarder les documents supplémentaires (ManyToMany)
            form.save_m2m()
            
            messages.success(request, f"Votre candidature pour '{offre.titre}' a été envoyée avec succès!")
            return redirect('candidature_detail', pk=candidature.pk)
    else:
        form = CandidatureForm(initial={'offre': offre}, user=request.user)
    
    context = {
        'form': form,
        'offre': offre,
        'deja_postule': deja_postule,
    }
    context['upload_url'] = reverse('add_document')
    context['document_list_url'] = reverse('document_list')
    
    return render(request, 'candidats/client/candidature/apply_job.html', context)

@login_required
def check_documents(request):
    """Vérifie si l'utilisateur a les documents nécessaires pour postuler"""
    user = request.user
    has_cv = user.documents.filter(
        type_document='CV', 
        est_actif=True, 
        est_supprime=False
    ).exists()
    
    has_lm = user.documents.filter(
        type_document='LM', 
        est_actif=True, 
        est_supprime=False
    ).exists()
    
    return JsonResponse({
        'has_cv': has_cv,
        'has_lm': has_lm,
        'cv_count': user.documents.filter(type_document='CV', est_actif=True, est_supprime=False).count(),
        'lm_count': user.documents.filter(type_document='LM', est_actif=True, est_supprime=False).count(),
    })


@login_required
def candidature_soft_delete(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    candidature = get_object_or_404(Candidature, pk=pk, candidat=request.user, est_supprime=False)
    
    if request.method == 'POST':
        form = SoftDeleteForm(request.POST)
        if form.is_valid():
            candidature.soft_delete()
            messages.success(request, "Candidature retirée avec succès")
            return redirect('candidature_list')
    else:
        form = SoftDeleteForm()
    
    return render(request, 'candidats/client/candidature/candidature_confirm_delete.html', {
        'candidature': candidature,
        'form': form
    })

# NOUVELLES VIEWS POUR ENTRETIENS ET ÉVALUATIONS
@login_required
def entretien_detail(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    entretien = get_object_or_404(Entretien, pk=pk, candidature__candidat=request.user, est_supprime=False)
    evaluation = getattr(entretien, 'evaluation', None)
    
    return render(request, 'candidats/client/entretien/entretien_detail.html', {
        'entretien': entretien,
        'evaluation': evaluation
    })

# Offres d'emploi
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def candidat_job_list(request):
    if not check_candidat(request.user):
        return redirect('access_denied')

    # Récupérer les paramètres de filtrage
    search_query = request.GET.get('search', '')
    lieu_query = request.GET.get('lieu', '')
    secteur_query = request.GET.get('secteur', '')
    type_contrat_query = request.GET.get('type_contrat', '')
    niveau_experience_query = request.GET.get('niveau_experience', '')
    salaire_min_query = request.GET.get('salaire_min', '')

    # Filtrer les offres
    offres = JobOffer.objects.filter(
        visible_sur_site=True
    ).annotate(
        is_open=Case(
            When(statut=JobStatus.OUVERT, then=1),
            default=0,
            output_field=IntegerField()
        ),
        est_expiree_db=Case(
            When(statut=JobStatus.EXPIRE, then=True),
            default=False,
            output_field=BooleanField()
        )
    ).order_by('-is_open', '-date_publication')

    # Appliquer les filtres
    if search_query:
        offres = offres.filter(
            Q(titre__icontains=search_query) |
            Q(mission_principale__icontains=search_query) |
            Q(profil_recherche__icontains=search_query) |
            Q(competences_qualifications__icontains=search_query)
        )

    if lieu_query:
        offres = offres.filter(lieu__icontains=lieu_query)

    if secteur_query:
        offres = offres.filter(secteur__icontains=secteur_query)

    if type_contrat_query:
        offres = offres.filter(type_offre=type_contrat_query)

    if niveau_experience_query:
        offres = offres.filter(experience_requise__icontains=niveau_experience_query)

    if salaire_min_query:
        try:
            salaire_min = int(salaire_min_query)
            offres = offres.filter(salaire__gte=salaire_min)
        except ValueError:
            pass

    # Pagination - 12 offres par page
    paginator = Paginator(offres, 12)
    page = request.GET.get('page')
    
    try:
        offres_paginated = paginator.page(page)
    except PageNotAnInteger:
        offres_paginated = paginator.page(1)
    except EmptyPage:
        offres_paginated = paginator.page(paginator.num_pages)

    # Préserver les paramètres de filtrage dans la pagination
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    context = {
        'offres': offres_paginated,
        'page_obj': offres_paginated,
        'is_paginated': paginator.num_pages > 1,
        'get_params': get_params.urlencode()
    }
    
    return render(request, 'candidats/client/candidat_job_list.html', context)

@login_required
def candidat_job_detail(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    offre = get_object_or_404(JobOffer, pk=pk)
    candidature = Candidature.objects.filter(
        candidat=request.user,
        offre=offre,
        est_supprime=False
    ).first() 
    
    deja_postule = candidature is not None
    today = timezone.now().date()
    
    # Ajouter la propriété est_expiree à l'offre
    offre.est_expiree_db = offre.statut == JobStatus.EXPIRE or (offre.date_limite and offre.date_limite < today)

    context = {
        'offre': offre,
        'deja_postule': deja_postule,
        'candidature': candidature,
        'today': today
    }
    
    if not deja_postule:
        context['form'] = CandidatureForm(user=request.user, initial={'offre': offre.pk})
    
    return render(request, 'candidats/client/candidat_job_detail.html', context)





# candidates/views_backoffice.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone

from authentication.models import User
from jobs.models import JobOffer
from .models import (
    ProfilCandidat, Diplome, ExperienceProfessionnelle,
    Document, Candidature, Entretien, Competence,
    EvaluationEntretien
)
from .forms import (
    CandidatFilterForm, CandidatureBackofficeForm,
    PlanifierEntretienForm, EntretienCompteRenduForm,
     CandidatureFilterForm,
    NoteInterneForm
)

def is_recruiter(user):
    """Vérifie si l'utilisateur fait partie de l'équipe recrutement"""
    return user.is_authenticated and user.role in ['admin', 'rh','stagiaire']

# ====================================================
# VUES TABLEAU DE BORD ET ACCUEIL
# ====================================================
@login_required
@user_passes_test(is_recruiter)
def backoffice_dashboard(request):
    """Tableau de bord simple du backoffice recrutement"""
    # Statistiques basiques seulement
    total_candidats = User.objects.filter(
        profil_candidat__isnull=False
    ).exclude(profil_candidat__est_supprime=True).count()
    
    total_candidatures = Candidature.objects.filter(est_supprime=False).count()
    
    # Offres actives (tous types: emploi, appel d'offres, autre)
    total_offres_actives = JobOffer.objects.filter(
        statut='OUVERT',  # Correction: 'OUVERT' au lieu de 'ouvert'
        visible_sur_site=True
    ).count()
    
    # Statistiques par type d'offre
    offres_par_type = JobOffer.objects.filter(
        statut='OUVERT',  # Correction: 'OUVERT' au lieu de 'ouvert'
        visible_sur_site=True
    ).values('type_offre').annotate(
        count=Count('id')
    )
    
    # Prochains entretiens (aujourd'hui et jours suivants)
    aujourdhui = timezone.now().date()
    prochains_entretiens = Entretien.objects.filter(
        est_supprime=False,
        date_prevue__date__gte=aujourdhui,  # Changement: >= aujourd'hui au lieu de ==
        statut__in=['PLANIFIE', 'CONFIRME']
    ).select_related('candidature__candidat', 'candidature__offre').order_by('date_prevue')[:5]
    
    # Entretiens aujourd'hui seulement (pour le compteur)
    entretiens_aujourdhui = Entretien.objects.filter(
        est_supprime=False,
        date_prevue__date=aujourdhui,
        statut__in=['PLANIFIE', 'CONFIRME']
    ).count()
    
    # Dernières candidatures
    dernieres_candidatures = Candidature.objects.filter(
        est_supprime=False
    ).select_related('candidat', 'offre').order_by('-date_postulation')[:5]
    
    context = {
        'today': timezone.now(),
        'total_candidats': total_candidats,
        'total_candidatures': total_candidatures,
        'total_offres_actives': total_offres_actives,
        'offres_par_type': offres_par_type,
        'prochains_entretiens': prochains_entretiens,
        'entretiens_aujourdhui': entretiens_aujourdhui, 
        'dernieres_candidatures': dernieres_candidatures,
    }
    
    return render(request, 'candidats/backoffice/dashboard.html', context)

# ====================================================
# VUES GESTION DES CANDIDATS (VUE 360)
# ====================================================
@login_required
@user_passes_test(is_recruiter)
def backoffice_candidat_list(request):
    """Liste des candidats avec filtres avancés"""
    candidats = User.objects.filter(
        Q(profil_candidat__isnull=False) & ~Q(profil_candidat__est_supprime=True)
    ).select_related('profil_candidat')
    
    form = CandidatFilterForm(request.GET or None)
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        competence = form.cleaned_data.get('competence')
        localite = form.cleaned_data.get('localite')
        niveau_etude = form.cleaned_data.get('niveau_etude')
        recherche_active = form.cleaned_data.get('recherche_active')
        disponible = form.cleaned_data.get('disponible')
        
        # Application des filtres
        if q:
            candidats = candidats.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q) |
                Q(profil_candidat__telephone__icontains=q) |
                Q(profil_candidat__telephone_second__icontains=q) |
                Q(profil_candidat__localite_souhaitee__icontains=q) |
                Q(profil_candidat__competences__nom__icontains=q) |
                Q(diplomes__competences__nom__icontains=q) |
                Q(experiences__competences__nom__icontains=q)
            ).distinct()
        
        if competence:
            source = form.cleaned_data.get('source_competence', '')
            
            # Create a Q object for competence filtering
            competence_q = Q()
            
            if source == 'profil' or not source:
                competence_q |= Q(profil_candidat__competences__in=competence)
            if source == 'diplomes' or not source:
                competence_q |= Q(diplomes__competences__in=competence)
            if source == 'experiences' or not source:
                competence_q |= Q(experiences__competences__in=competence)
                
            candidats = candidats.filter(competence_q).distinct()

        if localite:
            candidats = candidats.filter(
                Q(profil_candidat__adresse__ville__icontains=localite) |
                Q(profil_candidat__adresse__pays__icontains=localite) |
                Q(profil_candidat__localite_souhaitee__icontains=localite) |
                Q(diplomes__ville_obtention__icontains=localite) |
                Q(diplomes__pays_obtention__icontains=localite) |
                Q(experiences__lieu__icontains=localite) |
                Q(experiences__pays__icontains=localite)
            ).distinct()
        
        # New filter for education level
        if niveau_etude:
            # Get the index of the selected level to compare with database values
            niveau_index = next(i for i, (value, label) in enumerate(NIVEAU_CHOICES) if value == niveau_etude)
            # Get all levels that are equal or higher than the selected one
            niveaux_superieurs = [value for i, (value, label) in enumerate(NIVEAU_CHOICES) if i >= niveau_index]
            candidats = candidats.filter(diplomes__niveau__in=niveaux_superieurs).distinct()
        
        if recherche_active:
            candidats = candidats.filter(profil_candidat__recherche_active=True)
        
        if disponible:
            candidats = candidats.filter(profil_candidat__disponible=True)
    
    # Prefetch related data after filtering to optimize performance
    candidats = candidats.prefetch_related(
        'profil_candidat__competences',
        'diplomes__competences',
        'experiences__competences',
        'profil_candidat__adresse'
    ).distinct()
    
    # Pagination
    paginator = Paginator(candidats, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    
    return render(request, 'candidats/backoffice/candidats/candidat_list.html', context)

@login_required
@user_passes_test(is_recruiter)
def backoffice_candidat_detail(request, candidat_id):
    """Vue détaillée 360° d'un candidat"""
    candidat = get_object_or_404(User, id=candidat_id)
    
    # Vérifier que le candidat a un profil
    try:
        profil = candidat.profil_candidat
    except ProfilCandidat.DoesNotExist:
        messages.error(request, "Ce candidat n'a pas de profil complet.")
        return redirect('backoffice_candidat_list')
    
    # Récupérer toutes les données du candidat
    diplomes = candidat.diplomes.filter(est_supprime=False).order_by('-date_obtention')
    experiences = candidat.experiences.filter(est_supprime=False).order_by('-date_debut')
    
    # Documents triés par type et date
    documents = candidat.documents.filter(est_supprime=False, est_actif=True).order_by(
        'type_document', '-date_upload'
    )
    
    candidatures = candidat.candidatures.filter(est_supprime=False).select_related('offre')
    
    # Compétences
    competences = profil.competences.filter(est_supprime=False).distinct()
    
    context = {
        'candidat': candidat,
        'profil': profil,
        'diplomes': diplomes,
        'experiences': experiences,
        'documents': documents,
        'candidatures': candidatures,
        'competences': competences,
    }
    
    return render(request, 'candidats/backoffice/candidats/candidat_detail.html', context)


@login_required
@user_passes_test(is_recruiter)
def verifier_document(request, document_id):
    """Vue pour vérifier un document"""
    document = get_object_or_404(Document, id=document_id, est_supprime=False)
    
    if request.method == 'POST':
        try:
            document.verifier(request.user)
            messages.success(request, f"Le document '{document.nom}' a été vérifié avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la vérification du document: {str(e)}")
    
    # Rediriger vers la page du candidat
    return redirect('backoffice_candidat_detail', candidat_id=document.candidat.id)

@login_required
@user_passes_test(is_recruiter)
def annuler_verification_document(request, document_id):
    """Vue pour annuler la vérification d'un document"""
    document = get_object_or_404(Document, id=document_id, est_supprime=False)
    
    if request.method == 'POST':
        try:
            document.annuler_verification()
            messages.success(request, f"La vérification du document '{document.nom}' a été annulée.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'annulation de la vérification: {str(e)}")
    
    # Rediriger vers la page du candidat
    return redirect('backoffice_candidat_detail', candidat_id=document.candidat.id)
from django.http import FileResponse

@login_required
@user_passes_test(is_recruiter)
def telecharger_document(request, document_id):
    """Vue pour télécharger un document"""
    document = get_object_or_404(Document, id=document_id, est_supprime=False)

    response = FileResponse(document.fichier.open(), as_attachment=True, filename=document.nom)
    return response
# ====================================================
# VUES GESTION DES CANDIDATURES
# ====================================================
@login_required
@user_passes_test(is_recruiter)
def backoffice_candidature_list(request):
    """Liste des candidatures avec filtres"""
    candidatures = Candidature.objects.filter(
        est_supprime=False
    ).select_related('candidat', 'offre').order_by('-date_postulation')
    
    # Gestion de la barre de recherche
    search_query = request.GET.get('search')
    if search_query:
        candidatures = candidatures.filter(
            Q(candidat__first_name__icontains=search_query) |
            Q(candidat__last_name__icontains=search_query) |
            Q(candidat__email__icontains=search_query) |
            Q(offre__titre__icontains=search_query) |
            Q(offre__type_offre__icontains=search_query)  # Ajout du type d'offre dans la recherche
        )
    
    # Filtre par statut
    statut = request.GET.get('statut')
    if statut:
        candidatures = candidatures.filter(statut=statut)
    
    # Filtres par date
    date_min = request.GET.get('date_min')
    if date_min:
        try:
            candidatures = candidatures.filter(date_postulation__date__gte=date_min)
        except ValueError:
            pass
    
    date_max = request.GET.get('date_max')
    if date_max:
        try:
            candidatures = candidatures.filter(date_postulation__date__lte=date_max)
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(candidatures, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Préparer les choix de statut pour le template
    statut_choices = STATUT_CANDIDATURE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'statut_choices': statut_choices,
    }
    
    return render(request, 'candidats/backoffice/candidatures/candidature_list.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_candidature_detail(request, candidature_id):
    candidature = get_object_or_404(
        Candidature.objects.select_related('candidat', 'offre', 'cv_utilise', 'lettre_motivation'),
        id=candidature_id,
        est_supprime=False
    )
    
    # Formulaires
    form_candidature = CandidatureBackofficeForm(
        request.POST or None,
        instance=candidature
    )
    
    form_note = NoteInterneForm(request.POST or None)
    
    # Initialiser le formulaire d'entretien avec la candidature pré-remplie
    form_entretien = PlanifierEntretienForm(
        request.POST or None,
        initial={'candidature': candidature}
    )
    
    if request.method == 'POST':
        if 'update_candidature' in request.POST and form_candidature.is_valid():
            form_candidature.save()
            messages.success(request, "Candidature mise à jour avec succès.")
            return redirect('backoffice_candidature_detail', candidature_id=candidature.id)
        
        elif 'add_note' in request.POST and form_note.is_valid():
            # Ajouter la note aux notes existantes
            nouvelle_note = form_note.cleaned_data['note']
            is_important = form_note.cleaned_data['is_important']
            
            prefix = "🚨 NOTE IMPORTANTE:\n" if is_important else ""
            note_complete = f"{prefix}{nouvelle_note}\n\n— {request.user.get_full_name()}, {timezone.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            
            if candidature.notes:
                candidature.notes = note_complete + "---\n\n" + candidature.notes
            else:
                candidature.notes = note_complete
            
            candidature.save()
            messages.success(request, "Note ajoutée avec succès.")
            return redirect('backoffice_candidature_detail', candidature_id=candidature.id)
        
        elif 'planifier_entretien' in request.POST and form_entretien.is_valid():
            # Sauvegarder l'entretien avec le formulaire
            entretien = form_entretien.save(commit=False)
            entretien.statut = 'PLANIFIE'
            entretien.save()
            
            # Créer une note interne pour l'entretien
            note_contenu = f"""
            Entretien planifié pour: {candidature.offre.titre}
            Candidat: {candidature.candidat.get_full_name()}
            
            Détails de l'entretien:
            Type: {entretien.get_type_entretien_display()}
            Date: {entretien.date_prevue.strftime('%d/%m/%Y à %H:%M')}
            Durée: {entretien.duree_prevue} minutes
            Lieu: {entretien.lieu or 'Non spécifié'}
            Lien visio: {entretien.lien_video or 'Non spécifié'}
            Interlocuteurs: {entretien.interlocuteurs or 'Non spécifié'}
            
            Notes de préparation:
            {entretien.notes_preparation or 'Aucune note spécifiée'}
            """
            
            note_entretien = NoteInterne(
                expediteur=request.user,
                sujet=f"Entretien planifié - {candidature.candidat.get_full_name()} - {candidature.offre.titre}",
                contenu=note_contenu,
                niveau_urgence='medium',
                date_limite=entretien.date_prevue
            )
            note_entretien.save()
            
            # Ajouter tous les utilisateurs avec les rôles spécifiés comme destinataires
            roles_concernes = ['admin', 'rh', 'employe', 'stagiaire']
            utilisateurs_concernes = User.objects.filter(role__in=roles_concernes)
            
            for utilisateur in utilisateurs_concernes:
                NoteReception.objects.create(
                    note=note_entretien,
                    destinataire=utilisateur
                )
            
            # Mettre à jour la candidature
            candidature.statut = 'ENTRETIEN'
            candidature.save()
            
            messages.success(request, "Entretien planifié avec succès et note interne créée.")
            return redirect('backoffice_candidature_detail', candidature_id=candidature.id)
    
    context = {
        'candidature': candidature,
        'form_candidature': form_candidature,
        'form_note': form_note,
        'form_entretien': form_entretien,
    }
    
    return render(request, 'candidats/backoffice/candidatures/candidature_detail.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_candidature_quick_action(request, candidature_id, action):
    """Actions rapides sur les candidatures (changement de statut)"""
    candidature = get_object_or_404(Candidature, id=candidature_id, est_supprime=False)
    
    actions_valides = {
        'passer_entretien': 'ENTRETIEN',
        'accepter': 'ACCEPTE',
        'refuser': 'REFUSE',
        'mettre_en_attente': 'EN_REVUE',
    }
    
    if action in actions_valides:
        ancien_statut = candidature.statut
        nouveau_statut = actions_valides[action]
        
        candidature.statut = nouveau_statut
        candidature.save()
        
        messages.success(
            request, 
            f"Candidature passée de '{ancien_statut}' à '{nouveau_statut}'"
        )
    
    return redirect('backoffice_candidature_detail', candidature_id=candidature.id)

# ====================================================
# VUES GESTION DES ENTRETIENS
# ====================================================
@login_required
@user_passes_test(is_recruiter)
def backoffice_entretien_create(request, candidature_id=None):
    """Création manuelle d'un entretien avec création de note automatique"""
    # Initialiser avec ou sans candidature spécifique
    initial = {}
    candidature = None
    if candidature_id:
        candidature = get_object_or_404(Candidature, id=candidature_id, est_supprime=False)
        initial['candidature'] = candidature
    
    form = PlanifierEntretienForm(request.POST or None, initial=initial)
    
    if request.method == 'POST' and form.is_valid():
        try:
            entretien = form.save(commit=False)
            entretien.statut = 'PLANIFIE'
            entretien.save()
            
            # Mettre à jour la candidature
            candidature = entretien.candidature
            candidature.entretien_planifie = True
            candidature.date_entretien_prevue = entretien.date_prevue
            candidature.type_entretien_prevue = entretien.type_entretien
            candidature.statut = 'ENTRETIEN'
            candidature.save()
            
            # Créer une note interne pour l'entretien
            note_contenu = f"""
            Entretien planifié pour le poste: {candidature.offre.titre}
            Candidat: {candidature.candidat.get_full_name()}
            Type: {entretien.get_type_entretien_display()}
            Date: {entretien.date_prevue.strftime('%d/%m/%Y à %H:%M')}
            Durée: {entretien.duree_prevue} minutes
            
            Notes de préparation:
            {entretien.notes_preparation or 'Aucune note spécifiée'}
            
            Interlocuteurs: {entretien.interlocuteurs or 'Non spécifié'}
            Lieu/URL: {entretien.lieu or entretien.lien_video or 'Non spécifié'}
            """
            
            note_entretien = NoteInterne(
                expediteur=request.user,
                sujet=f"Entretien planifié - {candidature.candidat.get_full_name()} - {candidature.offre.titre}",
                contenu=note_contenu,
                niveau_urgence='medium',
                date_limite=entretien.date_prevue
            )
            note_entretien.save()
            
            # Ajouter tous les utilisateurs avec les rôles spécifiés comme destinataires
            roles_concernes = ['admin', 'rh', 'employe', 'stagiaire']
            utilisateurs_concernes = User.objects.filter(role__in=roles_concernes)
            
            for utilisateur in utilisateurs_concernes:
                NoteReception.objects.create(
                    note=note_entretien,
                    destinataire=utilisateur
                )
            
            # Lier la note à l'entretien (si votre modèle a cette relation)
            # entretien.note_liee = note_entretien
            # entretien.save()
            
            messages.success(request, "Entretien créé avec succès et note interne générée.")
            return redirect('backoffice_entretien_detail', entretien_id=entretien.id)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de l'entretien: {str(e)}")
    
    context = {
        'form': form,
        'candidature': candidature,
    }
    return render(request, 'candidats/backoffice/entretiens/entretien_create.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_entretien_edit(request, entretien_id):
    """Modifier un entretien existant avec mise à jour de note"""
    entretien = get_object_or_404(Entretien, id=entretien_id, est_supprime=False)
    
    if request.method == 'POST':
        form = PlanifierEntretienForm(request.POST, instance=entretien)
        if form.is_valid():
            ancienne_date = entretien.date_prevue
            ancien_type = entretien.type_entretien
            
            entretien = form.save()
            
            # Vérifier si les informations importantes ont changé
            date_modifiee = ancienne_date != entretien.date_prevue
            type_modifie = ancien_type != entretien.type_entretien
            
            # Si des informations importantes ont changé, créer une note de mise à jour
            if date_modifiee or type_modifie or form.cleaned_data.get('notes_preparation'):
                note_contenu = f"""
                Mise à jour de l'entretien pour: {entretien.candidature.offre.titre}
                Candidat: {entretien.candidature.candidat.get_full_name()}
                
                Modifications apportées:
                {"- Date modifiée" if date_modifiee else ""}
                {"- Type d'entretien modifié" if type_modifie else ""}
                {"- Notes de préparation mises à jour" if form.cleaned_data.get('notes_preparation') else ""}
                
                Nouveaux détails:
                Type: {entretien.get_type_entretien_display()}
                Date: {entretien.date_prevue.strftime('%d/%m/%Y à %H:%M')}
                Durée: {entretien.duree_prevue} minutes
                
                Notes de préparation:
                {entretien.notes_preparation or 'Aucune note spécifiée'}
                """
                
                note_mise_a_jour = NoteInterne(
                    expediteur=request.user,
                    sujet=f"Mise à jour entretien - {entretien.candidature.candidat.get_full_name()}",
                    contenu=note_contenu,
                    niveau_urgence='medium',
                    date_limite=entretien.date_prevue
                )
                note_mise_a_jour.save()
                
                # Notifier les utilisateurs concernés
                roles_concernes = ['admin', 'rh', 'employe', 'stagiaire']
                utilisateurs_concernes = User.objects.filter(role__in=roles_concernes)
                
                for utilisateur in utilisateurs_concernes:
                    NoteReception.objects.create(
                        note=note_mise_a_jour,
                        destinataire=utilisateur
                    )
            
            messages.success(request, "Entretien modifié avec succès.")
            return redirect('backoffice_entretien_detail', entretien_id=entretien.id)
    else:
        form = PlanifierEntretienForm(instance=entretien)
    
    context = {
        'form': form,
        'entretien': entretien,
        'title': 'Modifier l\'entretien'
    }
    return render(request, 'candidats/backoffice/entretiens/entretien_form.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_entretien_delete(request, entretien_id):
    """Supprimer un entretien avec création de note d'annulation"""
    entretien = get_object_or_404(Entretien, id=entretien_id, est_supprime=False)
    
    if request.method == 'POST':
        # Créer une note d'annulation avant de supprimer
        note_contenu = f"""
        Annulation de l'entretien prévu pour: {entretien.candidature.offre.titre}
        Candidat: {entretien.candidature.candidat.get_full_name()}
        Date prévue: {entretien.date_prevue.strftime('%d/%m/%Y à %H:%M')}
        Type: {entretien.get_type_entretien_display()}
        
        Raison de l'annulation: Entretien supprimé par {request.user.get_full_name()}
        Date de suppression: {timezone.now().strftime('%d/%m/%Y à %H:%M')}
        """
        
        note_annulation = NoteInterne(
            expediteur=request.user,
            sujet=f"Annulation entretien - {entretien.candidature.candidat.get_full_name()}",
            contenu=note_contenu,
            niveau_urgence='high',
            date_limite=timezone.now() + timedelta(days=1)
        )
        note_annulation.save()
        
        # Notifier les administrateurs et RH
        roles_concernes = ['admin', 'rh', 'employe', 'stagiaire']
        utilisateurs_concernes = User.objects.filter(role__in=roles_concernes)
        
        for utilisateur in utilisateurs_concernes:
            NoteReception.objects.create(
                note=note_annulation,
                destinataire=utilisateur
            )
        
        # Supprimer l'entretien
        entretien.soft_delete()
        
        # Mettre à jour le statut de la candidature
        candidature = entretien.candidature
        candidature.entretien_planifie = False
        candidature.date_entretien_prevue = None
        candidature.type_entretien_prevue = ''
        candidature.statut = 'RETIRE'  
        candidature.save()
        
        messages.success(request, "Entretien supprimé avec succès et note d'annulation créée.")
        return redirect('backoffice_entretien_list')
    
    context = {'entretien': entretien}
    return render(request, 'candidats/backoffice/entretiens/entretien_confirm_delete.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_entretien_list(request):
    """Liste des entretiens"""
    entretiens = Entretien.objects.filter(
        est_supprime=False
    ).select_related(
        'candidature__candidat__profil_candidat',  
        'candidature__offre'
    ).order_by('date_prevue')
    
    # Filtrage par statut
    statut_filter = request.GET.get('statut')
    if statut_filter:
        entretiens = entretiens.filter(statut=statut_filter)
    
    context = {
        'entretiens': entretiens,
        'statut_choices': STATUT_ENTRETIEN_CHOICES,
        'now': timezone.now(),
    }
    
    return render(request, 'candidats/backoffice/entretiens/entretien_list.html', context)

# views.py
@login_required
@user_passes_test(is_recruiter)
def backoffice_entretien_detail(request, entretien_id):
    """Détail d'un entretien (affichage seulement)"""
    entretien = get_object_or_404(
        Entretien.objects.select_related('candidature__candidat', 'candidature__offre'),
        id=entretien_id,
        est_supprime=False
    )
    
    context = {
        'entretien': entretien,
        'a_un_compte_rendu': entretien.a_un_compte_rendu_complet(),
    }
    
    return render(request, 'candidats/backoffice/entretiens/entretien_detail.html', context)

@login_required
@user_passes_test(is_recruiter)
def backoffice_entretien_compte_rendu(request, entretien_id):
    """Édition du compte-rendu d'entretien"""
    entretien = get_object_or_404(
        Entretien.objects.select_related('candidature__candidat', 'candidature__offre'),
        id=entretien_id,
        est_supprime=False
    )
    
    form = EntretienCompteRenduForm(
        request.POST or None,
        instance=entretien
    )
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Compte-rendu d'entretien enregistré.")
        return redirect('backoffice_entretien_detail', entretien_id=entretien.id)
    
    context = {
        'entretien': entretien,
        'form': form,
    }
    
    return render(request, 'candidats/backoffice/entretiens/entretien_compte_rendu.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_entretien_quick_action(request, entretien_id, action):
    """Actions rapides sur les entretiens"""
    entretien = get_object_or_404(Entretien, id=entretien_id, est_supprime=False)
    
    actions_valides = {
        'confirmer': 'CONFIRME',
        'annuler': 'ANNULE',
        'reporter': 'REPORTE',
        'terminer': 'TERMINE',
    }
    
    if action in actions_valides:
        entretien.statut = actions_valides[action]
        
        if action == 'terminer':
            entretien.date_reelle = timezone.now()
        
        entretien.save()
        messages.success(request, f"Entretien marqué comme {actions_valides[action]}")
    
    return redirect('backoffice_entretien_detail', entretien_id=entretien.id)


@login_required
@user_passes_test(is_recruiter)
def noteinterne_detail(request, note_id):
    """Affiche le détail d'une note interne"""
    note = get_object_or_404(NoteInterne, id=note_id)
    
    # Vérifier que l'utilisateur a accès à cette note
    if not request.user == note.expediteur and not note.receptions.filter(destinataire=request.user).exists():
        messages.error(request, "Vous n'avez pas accès à cette note.")
        return redirect('backoffice_candidature_list')
    
    context = {
        'note': note,
    }
    return render(request, 'notes/noteinterne_detail.html', context)

# ====================================================
# VUES ÉVALUATIONS
# ====================================================
@login_required
@user_passes_test(is_recruiter)
def backoffice_evaluation_create(request, entretien_id):
    """Création d'une évaluation pour un entretien"""
    entretien = get_object_or_404(Entretien, id=entretien_id, est_supprime=False)
    
    # Vérifier si une évaluation existe déjà
    if hasattr(entretien, 'evaluation'):
        messages.info(request, "Une évaluation existe déjà pour cet entretien.")
        return redirect('backoffice_evaluation_detail', entretien_id=entretien.id)
    
    form = EvaluationEntretienForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        evaluation = form.save(commit=False)
        evaluation.entretien = entretien
        evaluation.evaluateur = request.user
        evaluation.save()
        messages.success(request, "Évaluation créée avec succès.")
        return redirect('backoffice_evaluation_detail', evaluation_id=evaluation.id)
    
    context = {
        'entretien': entretien,
        'form': form,
    }
    
    return render(request, 'candidats/backoffice/evaluations/evaluation_create.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_evaluation_detail(request, evaluation_id):
    """Détail d'une évaluation d'entretien"""
    evaluation = get_object_or_404(EvaluationEntretien, id=evaluation_id)
    
    context = {
        'evaluation': evaluation,
    }
    
    return render(request, 'candidats/backoffice/evaluations/evaluation_detail.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_evaluation_edit(request, evaluation_id):
    """Modification d'une évaluation existante"""
    evaluation = get_object_or_404(EvaluationEntretien, id=evaluation_id)
    
    form = EvaluationEntretienForm(request.POST or None, instance=evaluation)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Évaluation modifiée avec succès.")
        return redirect('backoffice_evaluation_detail', evaluation_id=evaluation.id)
    
    context = {
        'evaluation': evaluation,
        'form': form,
        'entretien': evaluation.entretien,
    }
    
    return render(request, 'candidats/backoffice/evaluations/evaluation_edit.html', context)


@login_required
@user_passes_test(is_recruiter)
def backoffice_evaluations_rh(request):
    """
    Vue RH pour consulter toutes les évaluations et comptes-rendus d'entretien
    """
    # Filtres
    statut_filter = request.GET.get('statut', '')
    evaluateur_filter = request.GET.get('evaluateur', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    # Récupérer toutes les évaluations avec les entretiens associés
    evaluations = EvaluationEntretien.objects.select_related(
        'entretien', 
        'entretien__candidature',
        'entretien__candidature__candidat',
        'entretien__candidature__offre',
        'evaluateur'
    ).all()
    
    # Récupérer tous les entretiens avec compte-rendu complet
    entretiens_avec_compte_rendu = Entretien.objects.filter(
        est_supprime=False
    ).exclude(
        Q(feedback='') & 
        Q(points_abordes='') & 
        Q(questions_posees='') &
        Q(note_globale__isnull=True) &
        Q(points_positifs='') &
        Q(points_amelioration='') &
        Q(suite_prevue='')
    ).select_related(
        'candidature',
        'candidature__candidat',
        'candidature__offre'
    )
    
    # Appliquer les filtres sur les évaluations
    if statut_filter:
        evaluations = evaluations.filter(entretien__statut=statut_filter)
    
    if evaluateur_filter:
        evaluations = evaluations.filter(evaluateur_id=evaluateur_filter)
    
    if date_debut:
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
            evaluations = evaluations.filter(entretien__date_prevue__date__gte=date_debut_obj)
            entretiens_avec_compte_rendu = entretiens_avec_compte_rendu.filter(date_prevue__date__gte=date_debut_obj)
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
            evaluations = evaluations.filter(entretien__date_prevue__date__lte=date_fin_obj)
            entretiens_avec_compte_rendu = entretiens_avec_compte_rendu.filter(date_prevue__date__lte=date_fin_obj)
        except ValueError:
            pass
    
    # Récupérer la liste des évaluateurs pour le filtre
    evaluateurs = User.objects.filter(
        groups__name__in=['admin', 'rh','stagiaire']
    ).distinct()
    
    # Calcul manuel de la moyenne des notes (car note_moyenne est une propriété Python)
    notes_valides = [e.note_moyenne for e in evaluations if e.note_moyenne is not None]
    moyenne_notes = sum(notes_valides) / len(notes_valides) if notes_valides else 0
    
    # Calcul du taux de recommandation
    total_evaluations = evaluations.count()
    if total_evaluations > 0:
        taux_recommandation = evaluations.filter(recommander=True).count() / total_evaluations * 100
    else:
        taux_recommandation = 0
    
    # Récupérer les choix de statut depuis le champ du modèle
    statut_choices = Entretien._meta.get_field('statut').choices
    
    # Statistiques
    stats = {
        'total_evaluations': total_evaluations,
        'total_comptes_rendus': entretiens_avec_compte_rendu.count(),
        'moyenne_notes': round(moyenne_notes, 1),
        'taux_recommandation': round(taux_recommandation, 1),
    }
    
    context = {
        'evaluations': evaluations,
        'entretiens_avec_compte_rendu': entretiens_avec_compte_rendu,
        'evaluateurs': evaluateurs,
        'statut_choices': statut_choices,  # Utiliser les choix récupérés du champ
        'stats': stats,
        'filters': {
            'statut': statut_filter,
            'evaluateur': evaluateur_filter,
            'date_debut': date_debut,
            'date_fin': date_fin,
        }
    }
    
    return render(request, 'candidats/backoffice/evaluations/evaluations_rh.html', context)