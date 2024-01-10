from django.urls import path
from findomain.views import findomain_view

urlpatterns = [
    path('findomain/', findomain_view, name='findomain'),
]
