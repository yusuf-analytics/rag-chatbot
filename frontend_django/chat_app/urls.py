from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('collection/', views.chat_view, name='chat'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/create/', views.product_create, name='product_create'),
    path('dashboard/update/<int:pk>/', views.product_update, name='product_update'),
    path('dashboard/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('dashboard/sync/', views.trigger_sync, name='trigger_sync'),
]
