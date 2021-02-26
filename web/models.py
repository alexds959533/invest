from django.db import models


class Transactions(models.Model):
    CURRENCY = [('RUB', 'RUB'), ('USD', 'USD')]
    OPERATION = [
        ('buy', 'Покупка акций'),
        ('sell', 'Продажа акций'),
        ('currency_conversion', 'Конвертация валют'),
        ('commission', 'Комиссия'),
        ('deposit', 'Электронный перевод средств')
    ]
    ticker = models.CharField(max_length=10)
    date = models.DateField()
    operation = models.CharField(max_length=200, choices=OPERATION, default='deposit')
    amount = models.IntegerField()
    price = models.FloatField()
    commission = models.FloatField()
    currency = models.CharField(max_length=3, choices=CURRENCY,  default=2)

    def __str__(self):
        return 'ticker : {0}'.format(self.ticker)


class Dividends(models.Model):
    ticker = models.CharField(max_length=10)
    dividend_date = models.DateField()
    dividend_value = models.FloatField()
    payment_date = models.DateField()
    type = models.CharField(max_length=150)
    type_short = models.CharField(max_length=10)
    yeild = models.CharField(max_length=10)

    def __str__(self):
        return self.ticker + '-' + str(self.dividend_date)


class DividendPayments(models.Model):
    dividend = models.OneToOneField(Dividends, on_delete=models.CASCADE,
                                    primary_key=True)
    amount = models.IntegerField('Количество', blank=True)


class StockTimeSeries(models.Model):
    date = models.DateField()
    ticker = models.CharField(max_length=10)
    High = models.FloatField()
    Low = models.FloatField()
    Open = models.FloatField()
    Close = models.FloatField()
    Volume = models.BigIntegerField()

    def __str__(self):
        return str(self.date) + '-' + self.ticker + str(self.Close)


class OpenPosition(models.Model):
    ticker = models.CharField('Тикер', max_length=10)
    amount = models.IntegerField('Количество')
    price_avg = models.FloatField('Цена за единицу')
    base_cost = models.FloatField('Базовая стоимость')
    current_price = models.FloatField('Текущая цена')
    cost = models.FloatField('Стоимость')
    profit = models.FloatField('Прибыль')

    def __str__(self):
        return self.ticker + str(self.current_price)


class PortfolioCostChange(models.Model):
    date = models.DateField(primary_key=True)
    stock_cost = models.FloatField('Стоимость')
    rub_cost = models.FloatField('Рубль')
    usd_cost = models.FloatField('Доллар')
    deposit = models.FloatField('Депозит')
    commission = models.FloatField('Комиссия')
    dividend = models.FloatField('Дивиденды')
    stock_contain = models.JSONField('Состав', default=None, blank= True)

