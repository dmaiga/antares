# Dans candidats/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Candidature
from django.utils import timezone


@receiver(post_save, sender=Candidature)
def update_statut_entretien(sender, instance, **kwargs):
    """
    Met à jour automatiquement le statut de la candidature
    lorsque la date d'entretien est passée
    """
    if (instance.entretien_planifie and 
        instance.date_entretien_prevue and 
        instance.date_entretien_prevue < timezone.now() and
        instance.statut == 'ENTRETIEN'):
        # Ici vous pourriez changer le statut ou déclencher une action
        pass