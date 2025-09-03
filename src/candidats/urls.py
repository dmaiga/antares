from django.urls import path
from . import views
from .views import CustomPasswordChangeView

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard_candidat'),
   
    # Profil
    path('profil/', views.edit_profil, name='edit_profil'),
    path('profil/password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    
    # Diplômes
    path('diplomes/', views.diplome_list, name='diplome_list'),
    path('diplomes/ajouter/', views.diplome_create, name='add_diplome'),
    path('diplomes/<int:pk>/modifier/', views.diplome_update, name='edit_diplome'),
    path('diplomes/<int:pk>/supprimer/', views.diplome_soft_delete, name='delete_diplome'),  # CORRIGÉ
    
    # Expériences
    path('experiences/', views.experience_list, name='experience_list'),
    path('experiences/ajouter/', views.experience_create, name='add_experience'),
    path('experiences/<int:pk>/modifier/', views.experience_update, name='edit_experience'),
    path('experiences/<int:pk>/supprimer/', views.experience_soft_delete, name='delete_experience'),  # CORRIGÉ
    
    # Compétences
    path('competences/liste', views.competence_list, name='competence_list'),
    path('competences/create/', views.competence_create, name='competence_create'),
    path('competences/<int:pk>/update/', views.competence_update, name='competence_update'),
    path('competences/<int:pk>/delete/', views.competence_soft_delete, name='competence_delete'),  # CORRIGÉ
    
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/ajouter/', views.document_create, name='add_document'),
    path('documents/<int:pk>/modifier/', views.document_update, name='edit_document'),
    path('documents/<int:pk>/supprimer/', views.document_soft_delete, name='delete_document'),  # CORRIGÉ
    
    # Candidatures
    path('candidatures/', views.candidature_list, name='candidature_list'),
    path('candidatures/<int:pk>/', views.candidature_detail, name='candidature_detail'),
    path('candidatures/<int:pk>/retirer/', views.candidature_soft_delete, name='withdraw_candidature'),  # CORRIGÉ
    path('offre/<int:job_id>/postuler/', views.apply_job, name='apply_job'),
    path('check-documents/', views.check_documents, name='check_documents'),
    # Entretiens (NOUVEAU)
    path('entretiens/<int:pk>/', views.entretien_detail, name='entretien_detail'),  # NOUVEAU
    
    # Offres d'emploi
    path('offres_emploies/', views.candidat_job_list, name='candidat_job_list'),
    path('offres_detail/<int:pk>/', views.candidat_job_detail, name='candidat_job_detail'),

    ####
    #
    ####
    path('dashboard_backoffice/', views.backoffice_dashboard, name='backoffice_dashboard'),
    path('note/<int:note_id>/', views.noteinterne_detail, name='noteinterne_detail'),


    path('documents/<int:document_id>/verifier/', views.verifier_document, name='verifier_document'),
    path('documents/<int:document_id>/annuler-verification/', views.annuler_verification_document, name='annuler_verification_document'),
    path('documents/<int:document_id>/telecharger/', views.telecharger_document, name='telecharger_document'),
    # Candidats
    path('candidats_backoffice/', views.backoffice_candidat_list, name='backoffice_candidat_list'),
    path('candidats_backoffice/<int:candidat_id>/', views.backoffice_candidat_detail, name='backoffice_candidat_detail'),
    
    # Candidatures
    path('candidatures_backoffice/', views.backoffice_candidature_list, name='backoffice_candidature_list'),
    path('candidatures_backoffice/<int:candidature_id>/', views.backoffice_candidature_detail, name='backoffice_candidature_detail'),
    path('candidatures_backoffice/<int:candidature_id>/action/<str:action>/', views.backoffice_candidature_quick_action, name='backoffice_candidature_quick_action'),
    
    # Entretiens
    path('entretiens_backoffice/', views.backoffice_entretien_list, name='backoffice_entretien_list'),
    path('entretiens_backoffice/<int:entretien_id>/', views.backoffice_entretien_detail, name='backoffice_entretien_detail'),
    path('entretiens_backoffice/<int:entretien_id>/action/<str:action>/', views.backoffice_entretien_quick_action, name='backoffice_entretien_quick_action'),
    
    # Évaluations
    path('entretiens_backoffice/<int:entretien_id>/evaluation/', views.backoffice_evaluation_create, name='backoffice_evaluation_create'),
]