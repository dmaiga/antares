from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import JobOffer, JobStatus

class Command(BaseCommand):
    help = 'Met à jour le statut des offres expirées'

    def handle(self, *args, **options):
        # Mettre à jour les offres ouvertes dont la date limite est dépassée
        expired_count = JobOffer.objects.filter(
            statut=JobStatus.OUVERT,
            date_limite__lt=timezone.now().date()
        ).update(statut=JobStatus.EXPIRE)
        
        self.stdout.write(
            self.style.SUCCESS(f'{expired_count} offres marquées comme expirées')
        )