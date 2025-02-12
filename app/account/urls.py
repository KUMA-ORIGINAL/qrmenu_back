from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account.views import PasswordResetView, PasswordResetDoneView, \
    PasswordResetCompleteView, PasswordResetConfirmView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('password_reset/', PasswordResetView.as_view(), name='admin_password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
