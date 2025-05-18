from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PosterWebhookViewSet, PaymentWebhookViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'poster-webhook', PosterWebhookViewSet, basename='poster-webhook')
router.register('payment/webhook', PaymentWebhookViewSet, basename='payment_webhook')

urlpatterns = [
    path('', include(router.urls)),
]
