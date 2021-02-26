

from django.core.management.base import BaseCommand

from web.service.portfolio import PortfolioDescribe

class Command(BaseCommand):
    help = 'first start of project'

    def handle(self, *args, **options):
        pd = PortfolioDescribe()
        pd.portfolio_contain()
        pd.load_Stock_time_siries()


