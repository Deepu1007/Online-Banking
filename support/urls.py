from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_ticket, name='create_ticket'),
    path('my/', views.support_list, name='support_list'),

    # staff
    path('all/', views.all_tickets, name='all_tickets'),
    path('all/<int:pk>/status/<str:status>/', views.update_ticket_status, name='update_ticket'),
]
