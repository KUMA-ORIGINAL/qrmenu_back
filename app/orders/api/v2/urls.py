from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.api.v2 import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='orders-v2')
router.register(r'poster-webhook', views.PosterWebhookViewSet, basename='poster-webhook-v2')
router.register('payment/webhook', views.PaymentWebhookViewSet, basename='payment_webhook-v2')
router.register(r'clients', views.ClientViewSet, basename='client-v2')

urlpatterns = [
    path('', include(router.urls)),
    path("client/bonus/", views.ClientBonusAPIView.as_view(), name="client-bonus-v2"),
]
