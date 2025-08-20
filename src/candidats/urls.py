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
    path('diplomes/<int:pk>/supprimer/', views.diplome_delete, name='delete_diplome'),
    
    # Expériences
    path('experiences/', views.experience_list, name='experience_list'),
    path('experiences/ajouter/', views.experience_create, name='add_experience'),
    path('experiences/<int:pk>/modifier/', views.experience_update, name='edit_experience'),
    path('experiences/<int:pk>/supprimer/', views.experience_delete, name='delete_experience'),
    #competences
    path('competence/', views.competences_consolidees, name='competences_consolidees'),
    path('edit-profil/', views.edit_profil, name='edit_profil'),
    path('competences/liste', views.competence_list, name='competence_list'),
    path('competences/create/', views.competence_create, name='competence_create'),
    path('competences/<int:pk>/update/', views.competence_update, name='competence_update'),
    path('competences/<int:pk>/delete/', views.competence_delete, name='competence_delete'),
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/ajouter/', views.document_create, name='add_document'),
    path('documents/<int:pk>/modifier/', views.document_update, name='edit_document'),
    path('documents/<int:pk>/supprimer/', views.document_delete, name='delete_document'),
    
    # Candidatures
    path('candidatures/', views.candidature_list, name='candidature_list'),
    path('candidatures/<int:pk>/', views.candidature_detail, name='candidature_detail'),
    path('candidatures/<int:pk>/retirer/', views.candidature_withdraw, name='withdraw_candidature'),
    path('offres/<int:offre_id>/postuler/', views.candidature_create, name='apply_job'),
    #job url candidat

    path('offres_emploies/', views.candidat_job_list, name='candidat_job_list'),
    path('offres_detail/<int:pk>/', views.candidat_job_detail, name='candidat_job_detail'),
   
]