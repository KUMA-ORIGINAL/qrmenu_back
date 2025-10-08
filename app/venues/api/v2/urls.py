from django.urls import path, include
from rest_framework.routers import DefaultRouter

from venues.api.v2.views import PosterCallbackView, PosterAuthorizeView, BannerViewSet, VenueViewSet, CallWaiterView

router = DefaultRouter()
router.register('venues', VenueViewSet, basename='venues-v2')
router.register(r'banners', BannerViewSet, basename='banners-v2')

urlpatterns = [
    path('poster-auth/', PosterAuthorizeView.as_view(), name='poster_authorize-v2'),
    path('poster-oauth/callback/', PosterCallbackView.as_view(), name='poster_callback-v2'),
    path('', include(router.urls)),

    path("call-waiter/", CallWaiterView.as_view(), name="call_waiter-v2"),
]
