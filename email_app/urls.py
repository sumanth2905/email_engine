from django.urls import path
from . import views

urlpatterns = [
    path('create-account/', views.create_account, name='create_account'),
    path('get-emails/', views.get_user_emails, name='get_user_emails'),
    path('sync-emails', views.sync_user_emails, name='sync_user_emails'),
    path('connect-outlook/', views.connect_outlook, name='connect_outlook'),
]