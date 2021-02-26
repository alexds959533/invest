from django.contrib import admin
from web.models import Transactions, Dividend, OpenPosition,\
    DividendPayments, StockTimeSeries, PortfolioCostChange


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'date', 'amount', 'price')
    list_filter = ('ticker', 'operation')
    pass


@admin.register(Dividend)
class DividendAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'dividend_date', 'dividend_value')
    list_filter = ('ticker',)
    pass


@admin.register(OpenPosition)
class OpenPositionAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'amount', 'price_avg', 'current_price', 'profit')


@admin.register(StockTimeSeries)
class StockTimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('date', 'ticker', 'Close')
    list_filter = ('date', 'ticker')


@admin.register(PortfolioCostChange)
class PortfolioCostAdmin(admin.ModelAdmin):
    list_display = ('date', 'stock_cost', 'rub_cost', 'usd_cost',
                    'deposit', 'commission', 'dividend')
