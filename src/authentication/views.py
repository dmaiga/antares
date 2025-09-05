# authentication/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate ,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import forms 
from .forms import CreateUserForm,FichePosteForm
from .models import User
from logs.utils import enregistrer_action
from calendar import monthrange
from todo.models import FichePoste, Tache,TacheSelectionnee   


from django.utils import timezone

from todo.views import get_planning_context
from datetime import date, timedelta,datetime
from django.core.paginator import Paginator

from statistiques.utils import generate_graphs 
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from functools import wraps
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, EmployeeProfile

logger = logging.getLogger(__name__)

def is_rh_or_admin(user):
    return user.is_authenticated and user.role in ['admin', 'rh']




@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important ! Maintient la session
            messages.success(request, '🔐 Mot de passe modifié avec succès.')
            return redirect('dashboard')  # ou autre page
        else:
            messages.error(request, '❌ Veuillez corriger les erreurs.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'authentication/change_password.html', {'form': form})



def get_performance_class(percentage):
    if percentage is None:
        return 'no-data'
    if percentage >= 90:
        return 'Excellent'
    if percentage >= 70:
        return 'Très bon'
    if percentage >= 50:
        return 'Satisfaisant'
    return 'Insuffisant'

@login_required
@user_passes_test(is_rh_or_admin)
def dashboard_rh(request):
    try:
        # Filtre par défaut pour ne montrer que les employés et stagiaires
        users = User.objects.filter(role__in=['employe', 'stagiaire']).order_by('last_name')
        
        # Application des filtres
        poste = request.GET.get('poste')
        role = request.GET.get('role')
        nom = request.GET.get('nom')
        statut = request.GET.get('statut')
        
        if poste:
            users = users.filter(employeeprofile__poste_occupe__icontains=poste)
        if role:
            users = users.filter(role=role)
        if statut:
            users = users.filter(employeeprofile__statut=statut)
        if nom:
            users = users.filter(last_name__icontains=nom)

        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        jours_semaine = [start_of_week + timedelta(days=i) for i in range(5)]

        stats = []
        for user in users:
            # Get the employee profile using the correct related name
            try:
                employee_profile = user.employeeprofile
                fiche_poste = employee_profile.fiche_poste.titre if employee_profile.fiche_poste else 'N/A'
                statut_value = employee_profile.statut
                poste_occupe = employee_profile.poste_occupe
                telephone_pro = employee_profile.telephone_pro
                quartier = employee_profile.quartier
                contact_urgence = employee_profile.contact_urgence
                photo = employee_profile.photo  # CORRECTION: Photo depuis EmployeeProfile
            except EmployeeProfile.DoesNotExist:
                fiche_poste = 'N/A'
                statut_value = 'N/A'
                poste_occupe = 'N/A'
                telephone_pro = 'N/A'
                quartier = 'N/A'
                contact_urgence = 'N/A'
                photo = None  # CORRECTION: Photo à None
                employee_profile = None

            daily_data = []

            for day in jours_semaine:
                tasks_done = TacheSelectionnee.objects.filter(
                    user=user,
                    date_selection=day,
                    is_done=True
                ).count()
                percentage = round((tasks_done / 6) * 100) if tasks_done <= 6 else 100
                css_class = get_performance_class(percentage)
                daily_data.append({
                    'percentage': percentage,
                    'css_class': css_class,
                    'date': day
                })

            weekly_avg = round(sum(d['percentage'] for d in daily_data) / len(jours_semaine)) if jours_semaine else 0
            stats.append({
                'user': user,
                'employee_profile': employee_profile,
                'fiche_poste': fiche_poste,
                'statut': statut_value,
                'poste_occupe': poste_occupe,
                'telephone_pro': telephone_pro,
                'quartier': quartier,
                'contact_urgence': contact_urgence,
                'photo': photo,  # CORRECTION: Ajout de la photo
                'days': daily_data,  
                'weekly_avg': weekly_avg,
                'weekly_class': get_performance_class(weekly_avg),
            })

        context = {
            'stats': stats,
            'jours_semaine': jours_semaine,
            'users': users,
            'filters': {
                'poste': poste or '',
                'role': role or '',
                'nom': nom or '',
                'statut': statut or '',
            }
        }

        return render(request, 'authentication/dashboard_rh.html', context)

    except Exception as e:
        logger.error(f"Erreur dans dashboard RH : {str(e)}")
        raise


    
@login_required
@user_passes_test(is_rh_or_admin)
def supprimer_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id)
    fiche_id = tache.fiche_poste.id
    tache.delete()
    messages.success(request, "🗑️ Tâche supprimée.")
    return redirect('ajouter-taches-modele', fiche_id=fiche_id)

@login_required
@user_passes_test(is_rh_or_admin)
def modifier_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id)

    if request.method == 'POST':
        tache.titre = request.POST.get('titre')
        tache.description = request.POST.get('description')
        tache.save()
        messages.success(request, "✏️ Tâche modifiée.")
        return redirect('ajouter-taches-modele', fiche_id=tache.fiche_poste.id)

    return render(request, 'authentication/modifier_tache.html', {'tache': tache})


@login_required
@user_passes_test(is_rh_or_admin)
def create_modele_fiche_poste(request):
    if request.method == 'POST':
        form = FichePosteForm(request.POST)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.is_modele = True
            fiche.employe = None
            fiche.save()
            return redirect('liste-modeles-fiches')  
    else:
        form = FichePosteForm()
    return render(request, 'authentication/create_modele_fiche.html', {'form': form})

@login_required
@user_passes_test(is_rh_or_admin)
def supprimer_modele_fiche(request, fiche_id):
    fiche = get_object_or_404(FichePoste, id=fiche_id, is_modele=True)
    fiche.delete()
    messages.success(request, "Modèle de fiche supprimé avec succès.")
    return redirect('liste-modeles-fiches')

@login_required
@user_passes_test(is_rh_or_admin)
def liste_modeles_fiches(request):
    modeles = FichePoste.objects.filter(is_modele=True)
    return render(request, 'authentication/liste_modeles_fiches.html', {'modeles': modeles})

@login_required
@user_passes_test(is_rh_or_admin)
def ajouter_taches_modele(request, fiche_id):
    fiche = get_object_or_404(FichePoste, id=fiche_id, is_modele=True)

    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        duree_estimee = request.POST.get('duree_estimee')
        
        if titre:
            Tache.objects.create(
                fiche_poste=fiche,
                titre=titre,
                description=description,
                duree_estimee=duree_estimee if duree_estimee else None
            )
            messages.success(request, "✅ Tâche ajoutée avec succès.")
            return redirect('ajouter-taches-modele', fiche_id=fiche.id)

    return render(request, 'authentication/ajouter_taches_modele.html', {'fiche': fiche})


@login_required
@user_passes_test(is_rh_or_admin)
def detail_fiche_poste(request, fiche_id):
    fiche = get_object_or_404(FichePoste, id=fiche_id)
    return render(request, 'authentication/detail_fiche_poste.html', {'fiche': fiche})

@login_required
@user_passes_test(is_rh_or_admin)
def employees_view(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    statut_filter = request.GET.get('statut', '')
    department_filter = request.GET.get('department', '')
    
    
    # Start with users who have employee roles and prefetch the employee profile
    users = User.objects.filter(role__in=['employe', 'stagiaire'])\
                       .select_related('employeeprofile')\
                       .order_by('last_name')
    
    # Apply text search
    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(employeeprofile__poste_occupe__icontains=query) |
            Q(employeeprofile__ville__icontains=query)
        )
    
    # Apply role filter
    if role_filter:
        users = users.filter(role__iexact=role_filter)
    
    # Apply status filter (from EmployeeProfile)
    if statut_filter:
        users = users.filter(employeeprofile__statut__iexact=statut_filter)
    
    # Apply department filter (from EmployeeProfile)
    if department_filter:
        users = users.filter(employeeprofile__department__iexact=department_filter)
    


    # Get distinct departments for the filter dropdown
    departments = EmployeeProfile.objects.exclude(department='').values_list('department', flat=True).distinct()


    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'authentication/employees_view.html', {
        'page_obj': page_obj,
        'query': query,
        'departments': departments,
        
        'role_choices': User.ROLE_CHOICES,
        'statut_choices': EmployeeProfile.STATUT_CHOICES,
        'selected_role': role_filter,
        'selected_statut': statut_filter,
        'selected_department': department_filter,
       
    })






@login_required
def dashboard(request):
    today = timezone.localdate()
    filtre = request.GET.get("filtre", "all")

    # Base queryset - utilise les champs de TacheSelectionnee directement
    taches_auj = TacheSelectionnee.objects.filter(user=request.user, date_selection=today)
    taches_filtrees = taches_auj

    # Filtrage cohérent avec le modèle
    if filtre == "terminees":
        taches_filtrees = taches_auj.filter(is_done=True)  # Supprimez tache__
    elif filtre == "en_cours":
        taches_filtrees = taches_auj.filter(is_started=True, is_done=False)
    elif filtre == "pause":
        taches_filtrees = taches_auj.filter(is_paused=True, is_done=False)

    # Compteurs cohérents
    nb_total = taches_auj.count()
    nb_terminees = taches_auj.filter(is_done=True).count()
    nb_en_cours = taches_auj.filter(is_started=True, is_done=False).count()
    nb_pause = taches_auj.filter(is_paused=True, is_done=False).count()


    planning_ctx = get_planning_context(request)

    return render(request, 'authentication/dashboard.html', {
        'taches_auj': taches_filtrees,
        'nb_total': nb_total,
        'nb_terminees': nb_terminees,
        'nb_en_cours': nb_en_cours,
        'nb_pause': nb_pause,
        'filtre_actuel': filtre,
        **planning_ctx,
    })


from todo.models import FichePoste, Tache




def logout_user(request):
    
    logout(request)
    return redirect('login')





@login_required
@user_passes_test(is_rh_or_admin)
def assign_fiche_poste(request, user_id, fiche_id):
    user = get_object_or_404(User, id=user_id)
    fiche = get_object_or_404(FichePoste, id=fiche_id)
    
    if request.method == 'POST':
        user.fiche_poste = fiche
        user.save()
        messages.success(request, f"Fiche de poste {fiche.titre} attribuée")
    
    return redirect('edit-user-rh', user_id=user_id)



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def login_externe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')  # candidat, entreprise, consultant
        
        if email and password and user_type:
            user = authenticate(username=email, password=password)
            
            if user is not None:
                # VÉRIFICATION CRITIQUE : Cohérence user_type / user.role
                if is_role_consistent(user.role, user_type):
                    login(request, user)
                    return redirect_to_dashboard(user.role)
                else:
                    messages.error(request, f"Accès refusé : Ce compte ne correspond pas à l'espace {user_type}.")
            else:
                messages.error(request, "Email ou mot de passe incorrect")
        else:
            messages.error(request, "Veuillez remplir tous les champs")
    
    return render(request, 'auth/login_externe.html')

@csrf_protect
def login_interne(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if user is not None and user.role in ['admin', 'rh', 'employe', 'stagiaire']:
                login(request, user)
                return redirect_to_dashboard(user.role)
            else:
                messages.error(request, "Accès réservé au personnel interne")
        else:
            messages.error(request, "Veuillez remplir tous les champs")
    
    return render(request, 'auth/login_interne.html')

# Fonctions utilitaires
def is_role_consistent(user_role, user_type):
    """Vérifie la cohérence entre le rôle et le type choisi"""
    mapping = {
        'candidat': 'candidat',
        'entreprise': 'entreprise', 
        'consultant': 'consultant'
    }
    return user_role == mapping.get(user_type)

def redirect_to_dashboard(role):
    """Redirige vers le dashboard approprié"""
    dashboards = {
        'candidat': 'dashboard_candidat',
        'entreprise': 'dashboard-client',
        'consultant': 'dashboard_consultant',
        'admin': 'dashboard-rh',
        'rh': 'dashboard-rh',
        'employe': 'dashboard',
        'stagiaire': 'dashboard'
    }
    return redirect(dashboards.get(role, 'home'))



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .forms import CreateUserForm,  RHProfileForm,EmployeeProfileUpdateForm
from .models import User, EmployeeProfile

@login_required
def update_employee_profile(request):
    # Vérifier que l'utilisateur est un employé
    if not hasattr(request.user, 'employeeprofile') or request.user.role not in ['employe', 'stagiaire','rh']:
        messages.error(request, "Accès réservé aux employés.")
        return redirect('dashboard')
    
    profile = request.user.employeeprofile
    
    if request.method == 'POST':
        form = EmployeeProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Empêcher la modification de champs sensibles
            instance = form.save(commit=False)
            
            # S'assurer que l'utilisateur ne peut pas modifier ces champs
            protected_fields = [
                'matricule', 'statut', 'contract_type', 'salaire_brut', 
                'cout_total', 'notes_rh', 'points_forts', 'axes_amelioration',
                'taux_absenteeisme', 'productivite', 'satisfaction',
                'department', 'site', 'start_date', 'end_date', 'date_integration'
            ]
            
            for field in protected_fields:
                if field in form.changed_data:
                    messages.warning(request, f"Le champ {field} ne peut pas être modifié.")
                    return redirect('mon-profil')
            
            instance.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('mon-profil')
    else:
        form = EmployeeProfileUpdateForm(instance=profile)
    
    return render(request, 'authentication/employee_profile.html', {
        'form': form,
        'profile': profile
    })


@login_required 
@user_passes_test(is_rh_or_admin)
def edit_user_rh(request, user_id):
    user_cible = get_object_or_404(User, id=user_id)
    profile_cible, created = EmployeeProfile.objects.get_or_create(user=user_cible)

    if request.method == 'POST':
        form = RHProfileForm(request.POST, request.FILES, instance=profile_cible, user=user_cible)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Profil de {user_cible.get_full_name()} mis à jour")
            return redirect('employees-view')
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RHProfileForm(instance=profile_cible, user=user_cible)

    return render(request, 'authentication/edit_user_rh.html', {
        'form': form,
        'user_cible': user_cible
    })

@login_required
@user_passes_test(is_rh_or_admin)
def assigner_fiche_poste(request, user_id):
    user_cible = get_object_or_404(User, id=user_id)
    profile_cible = get_object_or_404(EmployeeProfile, user=user_cible)
    modeles_fiches = FichePoste.objects.filter(is_modele=True)

    if request.method == 'POST':
        fiche_id = request.POST.get('fiche_poste')
        if fiche_id:
            fiche_modele = get_object_or_404(FichePoste, id=fiche_id, is_modele=True)
            
            # Créer une copie de la fiche pour l'employé
            nouvelle_fiche = FichePoste.objects.create(
                titre=f"{fiche_modele.titre} - {user_cible.get_full_name()}",
                employe=user_cible,
                is_modele=False
            )
            
            # Copier les tâches
            for tache in fiche_modele.taches.all():
                Tache.objects.create(
                    fiche_poste=nouvelle_fiche,
                    titre=tache.titre,
                    description=tache.description,
                    duree_estimee=tache.duree_estimee
                )
            
            # Assigner la fiche à l'employé
            profile_cible.fiche_poste = nouvelle_fiche
            profile_cible.save()
            
            messages.success(request, "✅ Fiche de poste assignée avec succès")
            return redirect('edit-user-rh', user_id=user_id)

    return render(request, 'authentication/assigner_fiche_poste.html', {
        'user_cible': user_cible,
        'modeles_fiches': modeles_fiches
    })


@login_required
@user_passes_test(is_rh_or_admin)
def employees_view(request):
    users = User.objects.filter(role__in=['employe', 'stagiaire', 'rh'])\
                       .select_related('employeeprofile')\
                       .order_by('last_name')
    
    # Filtres (simplifiés)
    query = request.GET.get('q', '')
    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(employeeprofile__poste_occupe__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'authentication/employees_view.html', {
        'page_obj': page_obj,
        'query': query
    })


@login_required
@user_passes_test(is_rh_or_admin)
def user_detail(request):
    user_id = request.GET.get('id')
    user_cible = get_object_or_404(User, id=user_id)
    profile_cible = EmployeeProfile.objects.filter(user=user_cible).first()

    if not profile_cible:
        messages.error(request, "❌ Profil employé introuvable.")
        return redirect('dashboard-rh')

    # Journalisation
    enregistrer_action(request.user, 'CONSULT_USER_DETAIL', f"Consultation du profil de {user_cible.email}")

    return render(request, 'authentication/user_detail.html', {
        'user_cible': user_cible,
        'profile_cible': profile_cible
    })



@login_required
@user_passes_test(is_rh_or_admin)
def create_user_view(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            try:
                # Sauvegarder l'utilisateur
                user = form.save()
                generated_password = form.generated_password  # Récupérer le mot de passe
                
                fiche_modele = form.cleaned_data.get('fiche_poste')
                
                # Gestion de la fiche de poste si un modèle est sélectionné
                if fiche_modele:
                    nouvelle_fiche = FichePoste.objects.create(
                        titre=fiche_modele.titre,
                        employe=user,
                        is_modele=False
                    )
                
                    # Clonage des tâches
                    for tache in fiche_modele.taches.all():
                        Tache.objects.create(
                            fiche_poste=nouvelle_fiche,
                            titre=tache.titre,
                            description=tache.description,
                           
                            commentaire_rh=tache.commentaire_rh
                        )
                
                    # Affectation à l'EmployeeProfile
                    if hasattr(user, 'employeeprofile'):
                        user.employeeprofile.fiche_poste = nouvelle_fiche
                        user.employeeprofile.save()
                
                enregistrer_action(request.user, 'CREATE_USER', f"Création de {user.email}")
                
                # Stocker le mot de passe dans la session pour l'afficher sur la page de confirmation
                request.session['new_user_password'] = generated_password
                request.session['new_user_email'] = user.email
                
                return redirect('user_created_success')
                
            except Exception as e:
                messages.error(request, f"⚠️ Erreur lors de la création: {str(e)}")
                logger.error(f"Erreur création utilisateur: {str(e)}")
        else:
            messages.error(request, "⚠️ Erreur dans le formulaire. Veuillez corriger les champs.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CreateUserForm()
    
    return render(request, 'authentication/create_user.html', {'form': form})


# Nouvelle vue pour afficher la page de succès avec le mot de passe
@login_required
@user_passes_test(is_rh_or_admin)
def user_created_success(request):
    password = request.session.pop('new_user_password', None)
    email = request.session.pop('new_user_email', None)
    
    if not password or not email:
        return redirect('create-user')
    
    return render(request, 'authentication/user_created_success.html', {
        'email': email,
        'password': password
    })