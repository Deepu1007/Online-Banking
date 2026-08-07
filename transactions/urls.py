from django.urls import path
from . import views

urlpatterns = [
    path('transfer/', views.transfer_money, name='transfer'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('history/', views.history, name='history'),
]
