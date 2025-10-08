from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.api.v1 import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='orders')
router.register(r'poster-webhook', views.PosterWebhookViewSet, basename='poster-webhook')
router.register('payment/webhook', views.PaymentWebhookViewSet, basename='payment_webhook')

urlpatterns = [
    path('', include(router.urls)),
    path("client/bonus/", views.ClientBonusAPIView.as_view(), name="client-bonus"),
]
