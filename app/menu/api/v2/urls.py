from django.urls import path, include
from rest_framework.routers import DefaultRouter
from menu.api.v1 import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='categories-v2')
router.register(r'products', views.ProductViewSet, basename='products-v2')

urlpatterns = [
    path('', include(router.urls)),
    path("main-buttons/", views.MainButtonsAPIView.as_view(), name="main-buttons-v2")
]
