import pandas as pd
from django.http import HttpResponse
from task.tasks import adding_task

from django.shortcuts import render
from django.db import connection
from django.views.generic import TemplateView

from web.models import Transactions, Dividends, OpenPosition, DividendPayments, StockTimeSeries, PortfolioCostChange
from .forms import TransactionsForm


class TransactionView(TemplateView):
    def get(self, request):
        form = TransactionsForm()
        return render(request, 'transaction_post.html', {'form': form})

    def post(self, request):
        form = TransactionsForm(request.POST)
        # Проверка валидности данных формы:
        if form.is_valid():
            form.save().save()
        return render(request, 'transaction_post.html')

def index(request):
    a = adding_task.delay(10, 80)
    print(a)
    return render(request, 'main.html')


def transaction(request):
    query = 'SELECT *,amount * price as cost  FROM web_Transactions'
    transactions = Transactions.objects.raw(query)
    return render(request, 'transaction.html', {'transactions':transactions})


def stock_list(request):
    data = pd.read_sql_query(str(OpenPosition.objects.all().query), connection)
    data = data.sort_values('cost', ascending=False)
    all_data = []
    for i in range(data.shape[0]):
        temp = data.iloc[i]
        all_data.append(dict(temp))
    total_cost = data['cost'].sum()
    chart_data = []
    for i in range(data.shape[0]):
        chart_data.append({
            "values": [data.iloc[i]['cost']],

            "text": data.iloc[i]['ticker']
        }
        )
    return render(request, 'stock_list.html', {'stocks': all_data,
                                               'total_cost': total_cost,
                                               'chart_data': chart_data})


def stock_describe(request, ticker):
    query = f"SELECT id, payment_date  , dividend_value  FROM web_dividends where ticker = '{ticker}' and payment_date> '2010-01-01' order by payment_date"
    dividends = Dividends.objects.raw(query)
    dividend_data = []
    date_data = []
    for i in dividends:
        dividend_data.append(i.dividend_value)
        date_data.append(i.payment_date.year)
    return render(request, 'stock_describe.html', {'dividend_data': dividend_data,
                                                   'ticker': ticker,
                                                   'date_data': date_data})

def dividend(request):
    data = DividendPayments.objects.all()
    return render(request, 'dividend.html',  {'dividends': data})


def javascript(request):
    query = f'SELECT id, payment_date    FROM Dividends  order by payment_date'
    dividends = Dividends.objects.all()
    query = 'SELECT *, amount * price as cost  FROM Transactions'
    transactions = Transactions.objects.raw(query)
    dividend_data = []
    date_data = []
    for i in dividends:
        dividend_data.append(i.id)
        date_data.append(i.dividend_value)
        # dividend_data.append({str(i.payment_date): i.dividend})

    return render(request, 'javascript.html', {'dividend_data': dividend_data,
                                               'ticker': "AXP",
                                               'date_data': date_data})
