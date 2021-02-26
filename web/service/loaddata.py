
from datetime import timedelta, datetime
import json
import requests

from web.models import Transactions, DividendPayments, \
    PortfolioCostChange, StockTimeSeries, Dividend


class CostLoader:

    def __init__(self, date):
        self.date = date
        self.deposit = 0
        self.commission = 0
        self.stock_cost = 0
        self.dividend = 0
        try:
            yesterday = PortfolioCostChange.objects.get(date=date - timedelta(days=1))
            self.rub_cost = yesterday.rub_cost
            self.usd_cost = yesterday.usd_cost
            self.stock_contain = json.loads(yesterday.stock_contain)
        except PortfolioCostChange.DoesNotExist:
            self.rub_cost = 0
            self.usd_cost = 0
            self.stock_contain = {}

    def get_dividend_income(self):
        for div in Dividend.objects.filter(payment_date=self.date):
            amount = self.stock_contain.get(div.ticker)
            if amount:
                dividend_date = div.dividend_date
                # todo случай, когда вылетает за пределы начальной даты инвестирования нужно рассмотреть
                contain_on_dividend_json = PortfolioCostChange.objects.filter(
                    date=dividend_date)[0].stock_contain
                stock_contain_on_dividend = json.loads(contain_on_dividend_json)
                if div.ticker in stock_contain_on_dividend:
                    self.dividend += div.dividend_value * amount
                    DividendPayments.objects.get_or_create(amount=amount, dividend=div)
        if self.dividend:
            self.dividend = self.dividend * 0.9
            self.usd_cost += self.dividend

    def _get_last_open_day_price(self, tick, days=1):
        last_open_day = self.date - timedelta(days=days)
        sts_instance = StockTimeSeries.objects.filter(
            ticker=tick, date=last_open_day)
        if sts_instance:
            return sts_instance[0].Close
        else:
            return self._get_last_open_day_price(tick, days+1)

    def get_stock_cost(self, tick, cnt):
        date_format = self.date.strftime("%Y%m%d")
        token = 'pk_5a70318477f44dfcab83833546875e15'
        r = requests.get(f'https://cloud.iexapis.com//stable/stock/{tick}/'
                     f'chart/date/{date_format}?'
                     f'chartByDay=true&token={token}')
        try:
            data = r.json()[0]
            StockTimeSeries.objects.create(
                date=self.date,
                ticker=tick,
                High=data['uHigh'],
                Low=data['uLow'],
                Open=data['uOpen'],
                Close=data['uClose'],
                Volume=data['uVolume']
            )
            self.stock_cost += data['uClose'] * cnt
        except:
            self.stock_cost += self._get_last_open_day_price(tick) * cnt

    def get_portfolio_cost(self):
        for tick, cnt in self.stock_contain.items():
            # TODO Выходные хз че делать
            if self.date.dayofweek not in [5, 6]:
                sts = StockTimeSeries.objects.filter(
                    ticker=tick, date=self.date)
                if sts:
                    self.stock_cost += sts[0].Close * cnt
                else:
                    self.get_stock_cost(tick, cnt)
            else:
                self.stock_cost += self._get_last_open_day_price(tick, self.date.dayofweek - 4) * cnt

    def get_transaction(self):
        transactions = Transactions.objects.filter(date=self.date)
        if transactions:
            for event in transactions:
                operation = event.operation
                if operation == 'Электронный перевод средств':
                    self.rub_cost += event.amount
                    self.deposit = event.amount
                elif operation == 'Конвертация валют':
                    if event.ticker == 'USD.RUB':
                        self.commission += event.commission
                        self.usd_cost += event.amount
                        self.rub_cost -= event.amount * event.price
                    elif event.ticker == 'RUB.USD':
                        self.rub_cost -= event.amount
                        self.usd_cost += event.amount * event.price
                elif operation == 'Покупка акций':
                    if event.ticker not in self.stock_contain:
                        self.stock_contain[event.ticker] = event.amount
                    else:
                        self.stock_contain[event.ticker] = self.stock_contain[event.ticker] + event.amount
                    self.commission += event.commission
                    self.usd_cost -= event.amount * event.price
                    # TODO расписать случай продажа акций
                elif operation == 'Продажа акций':
                    self.commission += event.commission
                    self.usd_cost += event.amount * event.price
                elif operation == 'Комиссия':
                    self.commission += event.commission
        self.usd_cost -= self.commission

    def load_portfolio_date(self):
        self.get_transaction()
        if self.stock_contain:
            self.get_portfolio_cost()
            self.get_dividend_income()

        PortfolioCostChange.objects.get_or_create(
            date=self.date,
            stock_cost=self.stock_cost,
            rub_cost=self.rub_cost,
            usd_cost=self.usd_cost,
            deposit=self.deposit,
            commission=self.commission,
            dividend=self.dividend,
            stock_contain=json.dumps(self.stock_contain),
        )



