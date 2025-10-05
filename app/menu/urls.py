from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='categories')
router.register(r'products', views.ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path("main-buttons/", views.MainButtonsAPIView.as_view(), name="main-buttons")
]
