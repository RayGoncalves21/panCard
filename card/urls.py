from django.contrib import admin
from django.urls import include, path

from card.views import index

urlpatterns = [
    path('', index, name='home'),
    
    
]