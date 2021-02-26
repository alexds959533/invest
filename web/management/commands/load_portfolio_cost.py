from datetime import timedelta
import pandas as pd

from django.core.management.base import BaseCommand
from django.db.models import Max, Min

from web.models import PortfolioCostChange, Transactions
from web.service.loaddata import CostLoader


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        start_date = PortfolioCostChange.objects.aggregate(Max('date'))['date__max']
        if start_date:
            start_date = start_date + timedelta(days=1)
        else:
            start_date = Transactions.objects.aggregate(Min('date'))['date__min']
        date_range = pd.date_range(start_date, pd.to_datetime('today'))
        print(start_date)
        for dt in date_range:
            print(dt)
            cl = CostLoader(dt)
            cl.load_portfolio_date()
