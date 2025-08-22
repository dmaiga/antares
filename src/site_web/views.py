from django.shortcuts import render, redirect
from authentication.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import JobOffer
from django.shortcuts import render, get_object_or_404
#07_08
from django.core.paginator import Paginator
from django.db.models import Q
#09_08
from django.db.models import Q
from django.core.paginator import Paginator
from jobs.models import JobOffer, JobStatus
#12_08
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ExpertContactForm, GeneralContactForm
from django.core.mail import send_mail
from .forms import ExpertContactForm, GeneralContactForm
from antares_rh.settings import DEFAULT_FROM_EMAIL
from .models import ContactRequest

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ConsultantQuickEnrollmentForm, MissionFormSet


from django.shortcuts import render, get_object_or_404
from .models import ConsultantApplication
from django.utils import timezone

from antares_rh.settings import DEFAULT_FROM_EMAIL
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from django.conf import settings
from .forms import ConsultantQuickEnrollmentForm
from django.core.mail import send_mail

#14_08
#13_08


#15_O8

def consultant_info(request):
    if request.method == 'POST':
        form = ConsultantQuickEnrollmentForm(request.POST, request.FILES)
        formset = MissionFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            consultant = form.save()
            formset.instance = consultant
            formset.save()
            messages.success(request, "Votre inscription a bien été enregistrée !")
            send_consultant_email(consultant)
            return redirect('consultant-merci')
        else:
            # Debug: afficher les erreurs dans la console
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ConsultantQuickEnrollmentForm()
        formset = MissionFormSet()

    return render(request, 'site_web/consultant_info.html', {
        'form': form,
        'formset': formset
    })


# Fonction utilitaire pour l'email
def send_consultant_email(consultant):
    subject = f"Confirmation de votre inscription"
    message = f"""Bonjour {consultant.first_name},\n\n
    Merci pour votre inscription! Votre profil sera examiné sous 48h.\n
    Cordialement,\nL'équipe Antares """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [consultant.email],
        fail_silently=True
    )


#15_08

def consultant_merci(request):
    return render(request, 'site_web/consultant_merci.html')

 
#13_08
#14_08


def expert_contact_view(request):
    if request.method == 'POST':
        form = ExpertContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            # Envoyer l'email à l'expert
            send_expert_email(contact)
            
            messages.success(request, 'Votre demande a bien été envoyée à notre expert !')
            
    else:
        form = ExpertContactForm()

    return render(request, 'site_web/expert_form.html', {'form': form})

def contact(request):
    if request.method == 'POST':
        form = GeneralContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            # Envoyer l'email au service client
            send_general_email(contact)
            
            messages.success(request, 'Merci pour votre message ! Nous vous répondrons rapidement.')
            
    else:
        form = GeneralContactForm()

    return render(request, 'site_web/contact.html', {'form': form})

# Fonctions d'envoi d'email améliorées
def send_expert_email(contact):
    subject = f"[EXPERT] Nouvelle demande de {contact.first_name or 'Anonyme'}"
    recipient_list = ['expert@antares-rh.test']  # Liste des destinataires
    
    message = f"""
    Nouvelle demande d'expertise :
    
    Nom complet: {contact.first_name} {contact.last_name or ''}
    Entreprise: {contact.company or 'Non renseigné'}
    Secteur: {contact.sector or 'Non renseigné'}
    Contact: {contact.email} | {contact.phone or 'Non renseigné'}
    
    Message:
    {contact.message}
    
    ---
    Cet email a été envoyé depuis le formulaire expert.
    """
    
    send_mail(
        subject=subject,
        message=message.strip(),
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )

def send_general_email(contact):
    # Obtenir l'affichage du sujet depuis le formulaire
    subject_display = dict(GeneralContactForm.SUBJECT_CHOICES).get(contact.subject, contact.subject)
    
    subject = f"[CONTACT] {subject_display}"
    message = f"""
    Nouveau message via le formulaire général :
    
    De: {contact.first_name or 'Anonyme'} {contact.last_name or ''}
    Email: {contact.email}
    Sujet: {subject_display}
    
    Message:
    {contact.message}
    """
    
    send_mail(
        subject=subject,
        message=message.strip(),
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=['contact@antares-rh.test'],
        fail_silently=False,
    )
    

#12_08
#_____________________________________________________________________________
def jobs(request):
    # Récupération des paramètres
    search_query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    sector = request.GET.get('sector', '')
    contract_type = request.GET.get('contract_type', '')
    hide_expired = request.GET.get('hide_expired', 'false') == 'true'
    page_number = request.GET.get('page', 1)
    
    # Filtrage de base
    jobs = JobOffer.objects.filter(
        visible_sur_site=True,
        statut__in=[JobStatus.OUVERT, JobStatus.EXPIRE]
    ).exclude(
        statut=JobStatus.BROUILLON
    ).order_by('-date_publication')
    #pour masque les offres expirées
    if hide_expired:
        jobs = jobs.exclude(statut=JobStatus.EXPIRE)
    
    # Filtres supplémentaires
    if search_query:
        jobs = jobs.filter(
            Q(titre__icontains=search_query) |
            Q(mission_principale__icontains=search_query) |
            Q(profil_recherche__icontains=search_query) |
            Q(societe__icontains=search_query)
        )
    
    if location:
        jobs = jobs.filter(lieu__icontains=location)
    
    if sector:
        jobs = jobs.filter(secteur=sector)
    
    if contract_type:
        jobs = jobs.filter(type_offre=contract_type)
    
    # Pagination - 10 éléments par page
    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'jobs': page_obj,
        'search_query': search_query,
        'location': location,
        'sector': sector,
        'sector_choices': JobOffer.SectorChoices.choices,
        'contract_type': contract_type,
        'hide_expired': hide_expired,
        'status_choices': JobStatus.choices 
    }
    
    return render(request, 'site_web/public_jobs.html', context)

#
#_________________________________________________________________________________________________________________________
#

def public_job_offer_detail(request, pk):
    job = get_object_or_404(
        JobOffer, 
        pk=pk, 
        visible_sur_site=True,
        statut__in=['ouvert', 'expire'] 
    )
    
    # Suggestions d'autres offres
    related_jobs = JobOffer.objects.filter(
        visible_sur_site=True,
        statut='ouvert',
        secteur=job.secteur
    ).exclude(pk=pk).order_by('-date_publication')[:5]
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
        'is_expired': job.statut == 'expire'
    }
    
    return render(request, 'site_web/public_job_detail.html', context)

#
#_________________________________________________________________________________________________________________________
#
def home(request):
    featured_jobs = JobOffer.objects.filter(
        visible_sur_site=True,
        statut__in=['ouvert', 'expire']
    ).order_by('-date_publication')[:6]
    
    context = {
        'featured_jobs': featured_jobs
    }
    
    return render(request, 'site_web/index.html', context)

#09_08 
#07_08
#______________________________________________________________________________
def about(request):
    return render(request, 'site_web/about.html')



def teams(request):
    return render(request, 'site_web/teams.html')

def appointment(request):
    return render(request, 'site_web/appointment.html')



def recruteur_info(request):
    return render(request, 'site_web/recruteur_info.html')

def rejoindre_team(request):
    return render(request, 'site_web/rejoindre_team.html')




from site_web.forms import InscriptionCandidatForm
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils import timezone
# views.py
from django.contrib.auth import login
from django.contrib import messages

def candidat_register(request):
    featured_jobs = JobOffer.objects.filter(
        visible_sur_site=True,
        statut=JobStatus.OUVERT,
        date_limite__gte=timezone.now().date()
    )[:3]

    if request.method == 'POST':
        form = InscriptionCandidatForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            messages.success(
                request,
                f"Inscription réussie !  Vous pouvez maintenant vous connecter."
            )
            # Redirection vers login avec email pré-rempli
            return redirect(f"{reverse('login')}?email={user.email}&type=candidate")
    else:
        form = InscriptionCandidatForm()

    return render(request, 'site_web/candidate_registry.html', {
        'form': form,
        'featured_jobs': featured_jobs
    })

#22_08



