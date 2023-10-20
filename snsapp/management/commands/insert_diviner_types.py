from django.core.management.base import BaseCommand
from snsapp.models import *

class Command(BaseCommand):
    help = 'Inserts all DIVINER_TYPE_CHOICES into the database'

    def handle(self, *args, **kwargs):
        for type_code, type_name in DIVINER_TYPE_CHOICES:
            DivinerType.objects.get_or_create(name=type_code, defaults={'name': type_name})
        self.stdout.write(self.style.SUCCESS('Successfully inserted diviner types'))