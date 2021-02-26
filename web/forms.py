from django.forms import ModelForm
from .models import Transactions


class TransactionsForm(ModelForm):
    class Meta:
        exclude = ('id', )
        model = Transactions
