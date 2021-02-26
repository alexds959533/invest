
from django.contrib import admin
from django.urls import path
from web import views
from .views import TransactionView

admin.autodiscover()

urlpatterns = [
    path('', views.index),
    path('transaction', views.transaction),
    path('stock_list', views.stock_list),
    path('post', TransactionView.as_view()),
    path('stock_list/<str:ticker>', views.stock_describe),
    path('dividend', views.dividend),
    path('javascript', views.javascript),
]



