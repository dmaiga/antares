from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone

from .forms import JobOfferForm
from .models import JobOffer, JobStatus, JobType

def is_rh_or_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') in ['admin', 'rh','stagiaire','employee'])

# --- LISTE DES OFFRES ---
@login_required

def job_offer_list(request):
    # Récupération des paramètres
    status_filter = request.GET.get('status', 'all')
    type_filter = request.GET.get('type', 'all')
    search_query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    
    # Filtrage de base
    offers = JobOffer.objects.all().order_by('-date_publication')
    
    # Filtre par statut
    if status_filter != 'all':
        offers = offers.filter(statut=status_filter)
    
    # Filtre par type d'offre
    if type_filter != 'all':
        offers = offers.filter(type_offre=type_filter)
    
    # Recherche texte
    if search_query:
        offers = offers.filter(
            Q(titre__icontains=search_query) |
            Q(reference__icontains=search_query) |
            Q(societe__icontains=search_query) |
            Q(lieu__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination - 10 éléments par page
    paginator = Paginator(offers, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'offers': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'status_choices': JobStatus.choices,
        'type_choices': JobType.choices,
    }
    
    return render(request, 'jobs/job_offer_list.html', context)

# --- DETAIL D'UNE OFFRE ---
@login_required

def job_offer_detail(request, pk):
    offer = get_object_or_404(JobOffer, pk=pk)
    
    # Vérifier que l'utilisateur a le droit de voir cette offre
    if not (request.user.is_superuser or request.user.role in ['admin', 'rh']):
        return HttpResponseForbidden("Vous n'avez pas accès à cette ressource")
    
    return render(request, 'jobs/job_offer_detail.html', {'offer': offer})

# --- CREATION ---
@login_required

def job_offer_create(request):
    if request.method == 'POST':
        form = JobOfferForm(request.POST, request.FILES)
        if form.is_valid():
            job_offer = form.save(commit=False)
            job_offer.auteur = request.user
            
            # Définir le statut initial basé sur la visibilité
            if job_offer.visible_sur_site:
                job_offer.statut = JobStatus.OUVERT
            else:
                job_offer.statut = JobStatus.BROUILLON
            
            job_offer.save()
            messages.success(request, f"L'offre {job_offer.reference} a été créée avec succès.")
            return redirect('job-offer-detail', pk=job_offer.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = JobOfferForm()
    
    return render(request, 'jobs/job_offer_form.html', {
        'form': form,
        'title': 'Créer une nouvelle offre'
    })

# --- MISE A JOUR ---
@login_required

def job_offer_update(request, pk):
    job_offer = get_object_or_404(JobOffer, pk=pk)
    
    # Vérification des permissions (optionnel - pour plus de sécurité)
    if not (request.user.is_superuser or request.user.role in ['admin', 'rh']):
        return HttpResponseForbidden("Vous n'avez pas accès à cette ressource")
    
    if request.method == 'POST':
        form = JobOfferForm(request.POST, request.FILES, instance=job_offer)
        if form.is_valid():
            updated_offer = form.save(commit=False)
            
            # Mettre à jour le statut en fonction de la visibilité
            if updated_offer.visible_sur_site:
                if updated_offer.date_limite and updated_offer.date_limite < timezone.now().date():
                    updated_offer.statut = JobStatus.EXPIRE
                else:
                    updated_offer.statut = JobStatus.OUVERT
            else:
                updated_offer.statut = JobStatus.BROUILLON
            
            updated_offer.save()
            messages.success(request, f"L'offre {updated_offer.reference} a été mise à jour avec succès.")
            return redirect('job-offer-detail', pk=job_offer.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = JobOfferForm(instance=job_offer)
    
    return render(request, 'jobs/job_offer_form.html', {
        'form': form,
        'offer': job_offer,
        'title': f'Modifier l\'offre {job_offer.reference}'
    })

# --- SUPPRESSION ---
@login_required

def job_offer_delete(request, pk):
    job_offer = get_object_or_404(JobOffer, pk=pk)
    
    if not (request.user.is_superuser or request.user.role in ['admin', 'rh']):
        return HttpResponseForbidden("Vous n'avez pas accès à cette ressource")
    
    if request.method == 'POST':
        reference = job_offer.reference
        job_offer.delete()
        messages.success(request, f"L'offre {reference} a été supprimée avec succès.")
        return redirect('job-offer-list')
    
    return render(request, 'jobs/job_offer_confirm_delete.html', {'offer': job_offer})

# --- PUBLIER ---
@login_required

def job_offer_publish(request, pk):
    job_offer = get_object_or_404(JobOffer, pk=pk)
    
    if not (request.user.is_superuser or request.user.role in ['admin', 'rh']):
        return HttpResponseForbidden("Vous n'avez pas accès à cette ressource")
    
    job_offer.visible_sur_site = True
    if job_offer.date_limite and job_offer.date_limite < timezone.now().date():
        job_offer.statut = JobStatus.EXPIRE
    else:
        job_offer.statut = JobStatus.OUVERT
    
    job_offer.save()
    messages.success(request, f"L'offre {job_offer.reference} a été publiée.")
    return redirect('job-offer-detail', pk=pk)

# --- DE-PUBLIER ---
@login_required

def job_offer_unpublish(request, pk):
    job_offer = get_object_or_404(JobOffer, pk=pk)
    
    if not (request.user.is_superuser or request.user.role in ['admin', 'rh']):
        return HttpResponseForbidden("Vous n'avez pas accès à cette ressource")
    
    job_offer.visible_sur_site = False
    job_offer.statut = JobStatus.BROUILLON
    job_offer.save()
    messages.success(request, f"L'offre {job_offer.reference} a été retirée de la publication.")
    return redirect('job-offer-detail', pk=pk)

# --- VUE PUBLIQUE POUR LE SITE ---
def job_offer_public_list(request):
    """Vue pour afficher les offres sur le site public"""
    offers = JobOffer.objects.filter(
        visible_sur_site=True,
        statut=JobStatus.OUVERT
    ).order_by('-date_publication')
    
    # Filtrage optionnel
    type_filter = request.GET.get('type', 'all')
    if type_filter != 'all':
        offers = offers.filter(type_offre=type_filter)
    
    search_query = request.GET.get('q', '')
    if search_query:
        offers = offers.filter(
            Q(titre__icontains=search_query) |
            Q(mission_principale__icontains=search_query) |
            Q(lieu__icontains=search_query) |
            Q(secteur__icontains=search_query)
        )
    
    paginator = Paginator(offers, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/public_job_list.html', {
        'offers': page_obj,
        'type_choices': JobType.choices,
        'type_filter': type_filter,
        'search_query': search_query
    })

def job_offer_public_detail(request, pk):
    """Vue pour afficher le détail d'une offre sur le site public"""
    offer = get_object_or_404(
        JobOffer.objects.filter(
            visible_sur_site=True,
            statut=JobStatus.OUVERT
        ),
        pk=pk
    )
    
    return render(request, 'jobs/public_job_detail.html', {'offer': offer})