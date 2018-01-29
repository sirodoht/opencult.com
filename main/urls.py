from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = 'Open Cult administration'
app_name = 'main'

urlpatterns = [
    # /
    path('', views.index, name='index'),

    # /login/
    path('login/', views.get_login, name='login'),

    # /auth/
    path('auth/', views.token_post, name='auth'),

    # /logout/
    path('logout/', views.get_logout, name='logout'),
]
