from django.urls import path

from menu.api.v1.views import get_categories
from venues.api.v1.views import get_halls_by_spot, get_spots


urlpatterns = [
    path('get-halls/', get_halls_by_spot, name='admin_get_halls_by_spot'),
    path('get_spots/', get_spots, name='get_spots'),
    path('get_categories/', get_categories, name='get_categories'),
]
