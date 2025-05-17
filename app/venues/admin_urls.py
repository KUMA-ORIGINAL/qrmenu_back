from django.urls import path

from .views import  get_halls_by_spot

urlpatterns = [
    path('get-halls/', get_halls_by_spot, name='admin_get_halls_by_spot'),
]
