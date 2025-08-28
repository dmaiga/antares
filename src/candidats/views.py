from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Exists, OuterRef
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from authentication.models import User
from jobs.models import JobOffer
from .models import (
    ProfilCandidat, Diplome, ExperienceProfessionnelle,
    Document, Candidature, Adresse, Entretien, Competence,
    EvaluationEntretien  # NOUVEAU MODÈLE
)
from .forms import (
    ProfilCandidatForm, DiplomeForm, ExperienceForm,
    DocumentForm, CandidatureForm, AdresseForm,
    UserUpdateForm, CompetenceForm, EntretienForm,
    EntretienFeedbackForm, EvaluationEntretienForm,  # NOUVEAUX FORMULAIRES
    SoftDeleteForm  # NOUVEAU FORMULAIRE
)

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
    
    # Sous-requête pour vérifier les candidatures
    candidature_exists = Candidature.objects.filter(
        candidat=request.user,
        offre=OuterRef('pk')
    )
    
    # Annoter les offres avec l'information de candidature
    offres_recentes = JobOffer.objects.filter(
        statut='ouvert',
        visible_sur_site=True
    ).annotate(
        deja_postule=Exists(candidature_exists)
    ).order_by('-date_publication')[:5]
    
    context = {
        'profil': profil,
        'diplomes': request.user.diplomes.filter(est_supprime=False),
        'experiences': request.user.experiences.filter(est_supprime=False).order_by('-date_debut'),
        'competences': profil.competences.filter(est_supprime=False),
        'documents': request.user.documents.filter(est_supprime=False),
        'candidatures': request.user.candidatures.filter(est_supprime=False).select_related('offre'),
        'offres_recentes': offres_recentes
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

@login_required
def candidature_create(request, offre_id):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    offre = get_object_or_404(JobOffer, pk=offre_id)
    
    if Candidature.objects.filter(candidat=request.user, offre=offre, est_supprime=False).exists():
        messages.warning(request, "Vous avez déjà postulé à cette offre")
        return redirect('candidature_list')
    
    if request.method == 'POST':
        form = CandidatureForm(request.POST, user=request.user)
        if form.is_valid():
            candidature = form.save(commit=False)
            candidature.candidat = request.user
            candidature.offre = offre
            candidature.save()
            form.save_m2m()  # Pour les documents supplémentaires
            messages.success(request, "Candidature envoyée avec succès !")
            return redirect('candidature_list')
    else:
        form = CandidatureForm(user=request.user, initial={'offre': offre.pk})
    
    return render(request, 'candidats/client/candidature/postuler_offre.html', {
        'form': form,
        'offre': offre
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
@login_required
def candidat_job_list(request):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    offres = JobOffer.objects.filter(
        statut='ouvert',
        visible_sur_site=True
    ).order_by('-date_publication')
    
    return render(request, 'candidats/client/candidat_job_list.html', {'offres': offres})

@login_required
def candidat_job_detail(request, pk):
    if not check_candidat(request.user):
        return redirect('access_denied')
    
    offre = get_object_or_404(JobOffer, pk=pk)
    deja_postule = Candidature.objects.filter(
        candidat=request.user,
        offre=offre,
        est_supprime=False
    ).exists()
    
    context = {
        'offre': offre,
        'deja_postule': deja_postule
    }
    
    if not deja_postule:
        context['form'] = CandidatureForm(user=request.user, initial={'offre': offre.pk})
    
    return render(request, 'candidats/client/candidat_job_detail.html', context)