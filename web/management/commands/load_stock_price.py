import requests

from web.models import OpenPosition
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        token = 'bqmtruvrh5re7283h69g'
        for position in OpenPosition.objects.all():
            tick = position.ticker
            price = requests.get(f'https://finnhub.io/api/v1/quote?'
                                 f'symbol={tick}&token={token}').json()['c']
            position.current_price = price
            position.cost = price * position.amount
            position.profit = position.cost / position.base_cost
            position.save()
        # rub_usd = requests.get(f'https://finnhub.io/api/v1/forex/rates?base=USD&'
        #                        f'token={token}').json()['quote']['RUB']
