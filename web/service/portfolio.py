import pandas as pd
import pandas_datareader.data as wb
from datetime import datetime
import requests


from django.db import connection
from django.db.models import Max

from web.models import Transactions, Dividend, \
    OpenPosition, DividendPayments, PortfolioCostChange, StockTimeSeries

# TODO уйти от пандаса


class PortfolioDescribe:
    ''' вызов 1 раза при первом запуске проекта,
    необходи для формирования стартовых таблиц '''

    def __init__(self):
        self.transaction = pd.read_sql_query(
            str(Transactions.objects.all().query), connection, index_col='id')
        self.dividends = pd.read_sql_query(
            str(Dividend.objects.all().query), connection, index_col='id')

    def portfolio_contain(self, ticker=None, date=None):
        """     функция для агрегирования информации и представление состава портфеля
                необходимо для первоначального заполения OpenPosition функция load_open_position()"""
        cursor = connection.cursor()
        query = """SELECT buy.ticker, 
                        total / buy.amount price, 
                        case when sale.amount is Null then buy.amount else  buy.amount - sale.amount  end amount 
                FROM (select ticker, sum(amount) amount, sum(price * amount) total from public.transactions 
                    where operation_type = 'Покупка акций'
                    group by ticker) as buy 
                left join (
                    select ticker, sum(amount) amount from public.transactions 
                    where operation_type = 'Продажа акций'
                    group by ticker) as sale on buy.ticker = sale.ticker
                where case when sale.amount is Null then buy.amount else  buy.amount - sale.amount  end > 0
                order by ticker """
        cursor.execute(query)
        agg_stocks = cursor.fetchall()
        for stock in agg_stocks:
            OpenPosition.objects.create(
                ticker=stock[0],
                amount=stock[2],
                price_avg=stock[1],
                base_cost=stock[2] * stock[1],
                current_price=0,
                cost=0,
                profit=0
                )
    # todo Переделать под первый запуск
    def load_Stock_time_siries(self):
        query = "SELECT id , ticker   FROM Transactions where operation_type = 'Покупка акций'"
        ticker_list = list(set([i.ticker for i in Transactions.objects.raw(query)]))
        start = StockTimeSeries.objects.all().aggregate(Max('date'))['date__max']  # + timedelta(days=1)
        if not start:
            start = datetime(2000, 1, 1)
        end = datetime.today()
        for tick in ticker_list:
            stock_data = wb.DataReader(tick, 'yahoo', start, end)
            stock_data = stock_data.drop(stock_data[stock_data.index == start].index)
            for i in range(len(stock_data)):
                StockTimeSeries.objects.create(
                    date=stock_data.index[i],
                    ticker=tick,
                    High=stock_data.iloc[i]['High'],
                    Low=stock_data.iloc[i]['Low'],
                    Open=stock_data.iloc[i]['Open'],
                    Close=stock_data.iloc[i]['Close'],
                    Volume=stock_data.iloc[i]['Volume']
                )


# вынести во въюху
def get_dividend_new_conpany(self, ticker):
    tickers = [q.ticker for q in Dividend.objects.distinct('ticker')]
    if ticker not in tickers:
        r = requests.get(
            f'https://fcsapi.com/api-v2/stock/dividend?symbol={ticker}&access_key='
            f'v4V4byeLO0y9gWSusZooGvw2LA5eZON7lZBQocPM6mqWpteqWT').json()
        # todo загрузка напрямую из JSON в модель
        data = r['response'][0]['data']
        dividend = pd.DataFrame(data).T
        for i in range(len(dividend)):
            Dividend.objects.create(
                ticker=ticker,
                dividend_date=dividend.iloc[i]['dividend_date'],
                dividend_value=dividend.iloc[i]['dividend'],
                payment_date=dividend.iloc[i]['payment_date'],
                type=dividend.iloc[i]['type'],
                type_short=dividend.iloc[i]['type_short'],
                yeild=dividend.iloc[i]['yeild']
            )



