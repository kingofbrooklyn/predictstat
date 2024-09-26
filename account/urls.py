"""account URL Configuration"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='account-home'),\
    path('register/', views.register, name='account-register'),\
    path('login/', views.login_, name='account-login'),\
    path('logout/', views.logout_, name='account-logout'),\
        
    path('account-delete-workspace', views.delete_workspace, name='account-delete-workspace'),\
    path('account-update-workspace', views.update_workspace, name='account-update-workspace'),\
]
