from django.core.management.base import BaseCommand
from site_web.models import MissionDomain
import json

class Command(BaseCommand):
    help = 'Met à jour les domaines de mission à partir des candidatures'

    def handle(self, *args, **options):
        from site_web.models import ConsultantApplication
        
        # Extraction des termes des missions
        domain_counts = {}
        for app in ConsultantApplication.objects.all():
            if app.missions_data:
                for mission in app.missions_data:
                    domain = mission.get('type', '').split(':')[0].strip()
                    if domain:
                        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Création/mise à jour des domaines
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            MissionDomain.objects.get_or_create(
                name=domain,
                defaults={'is_active': count > 2}  # Active si fréquent
            )
            self.stdout.write(f"{domain}: {count} occurrences")