from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
import numpy as np
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand
from django.db.models import Max, Min

from web.models import Dividend


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        tickers = [q.ticker for q in Dividend.objects.distinct('ticker')]
        for tick in tickers:
            url = f'https://ycharts.com/companies/{tick}/dividend'
            try:
                req = Request(url)
                webpage = urlopen(req).read()
                soup = BeautifulSoup(webpage)
                info = soup.find('table', class_="histDividendDataTable").text.split()
                data = np.array(info)[9:]
                rows = int(len(data) / 6)
                data.shape = (rows, 6)
                for row in data:
                    # ['dividend_date', 'Record Date', 'payment_date', 'Declared Date', 'Type', 'dividend_value']
                    dividend_date = datetime.strptime(row[0], '%m/%d/%Y')
                    payment_date = datetime.strptime(row[2], '%m/%d/%Y')
                    dividend_value = float(row[5])
                    if dividend_date.date() > Dividend.objects.filter(
                            ticker=tick).aggregate(Max('dividend_date'))['dividend_date__max']:
                        Dividend.objects.create(
                            ticker=tick,
                            dividend_date=dividend_date,
                            dividend_value=dividend_value,
                            payment_date=payment_date,
                            type='Quarterly',
                            type_short='3M',
                            yeild='-'
                        )
                    else:
                        break

            except urllib.error.HTTPError as err:
                pass