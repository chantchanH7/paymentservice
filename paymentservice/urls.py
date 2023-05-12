from django.urls import path
from paymentservice import views

urlpatterns = [
    path('register/', views.Register, name='register'),
    path('login/', views.Login, name='login'),
    path('order/', views.Orders, name='order'),
    path('pay/', views.Pay, name='pay'),
    path('refund/', views.Refund, name='refund'),
    path('balance/', views.Balance, name='balance'),
    path('deposit/', views.Deposit, name='deposit'),
]
