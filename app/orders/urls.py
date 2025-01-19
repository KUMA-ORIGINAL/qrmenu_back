from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PosterWebhookViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'poster-webhook', PosterWebhookViewSet, basename='poster-webhook')

urlpatterns = [
    path('', include(router.urls)),
]
