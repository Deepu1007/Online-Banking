from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), 
         name="password_reset"),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), 
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), 
         name="password_reset_confirm"),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), 
         name="password_reset_complete"),

    # staff
    path('staff/customers/', views.customer_list, name='staff_customers'),
    path('staff/customers/<int:pk>/approve/', views.approve_customer, name='approve_customer'),
    path('staff/customers/<int:pk>/reject/', views.reject_customer, name='reject_customer'),
    path('staff/customers/<int:pk>/toggle/', views.open_close_account, name='toggle_account'),

    # child account URLs
    path('child/create/', views.create_child_account, name='create_child'),
    path('child/<int:pk>/transactions/', views.child_transactions, name='child_transactions'),
    path('child/<int:pk>/toggle/', views.toggle_child_account, name='toggle_child_account'),

    # terminate account URLS
    path("terminate-child/<int:child_id>/", views.terminate_child, name="terminate_child"),

    #deposite and withdraw
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
]
