from django.core.management.base import BaseCommand
from snsapp.models import *

class Command(BaseCommand):
    help = 'Inserts all SHOP_LABEL into the database'

    def handle(self, *args, **kwargs):
        for cost_code, cost_name in SHOP_LABEL:
            Cost.objects.get_or_create(label=cost_code, defaults={'label': cost_name})
        self.stdout.write(self.style.SUCCESS('Successfully inserted cost'))