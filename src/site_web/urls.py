from django.urls import path
from . import views

urlpatterns = [
    #12_08
    path('expert/', views.expert_contact_view, name='public-contact-expert'),
    path('contact/', views.contact, name='contact'),
    path('consultant_info/', views.consultant_info, name='consultant-info'),
    path('consultant/merci/', views.consultant_merci, name='consultant-merci'),

    #12_08
    
    #07_08
    path('emplois/<int:pk>/', views.public_job_offer_detail, name='public-job-offer-detail'),
    #07_08
    #_____________________________________________________
    path('home', views.home, name='home'),
    path('about/', views.about, name='about'),

    path('jobs/', views.jobs, name='jobs'),
  
    path('teams', views.teams, name='teams'),
     path('appointment', views.appointment, name='appointment'),

    path('candidat/inscription/', views.candidat_register, name='candidate-registry'),
   
    #path('recruteur_info/', views.recruteur_info, name='recruteur-info'),
    
    path('rejoindre_team/', views.rejoindre_team, name='rejoindre-team'),






]