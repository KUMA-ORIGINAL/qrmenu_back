from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PosterCallbackView, PosterAuthorizeView

router = DefaultRouter()

urlpatterns = [
    path('poster-auth/', PosterAuthorizeView.as_view(), name='poster_authorize'),
    path('poster-oauth/callback/', PosterCallbackView.as_view(), name='poster_callback'),
    path('', include(router.urls)),
]
