import logging

import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from django.shortcuts import redirect

from services.pos_service_factory import POSServiceFactory
from venues.models import Venue, POSSystem
from venues.api.v1.serializers import OAuthCallbackSerializer

logger = logging.getLogger(__name__)

User = get_user_model()

class PosterAuthorizeView(APIView):
    def get(self, request, *args, **kwargs):
        application_id = settings.POSTER_APPLICATION_ID
        redirect_uri = settings.POSTER_REDIRECT_URI

        auth_url = (f"https://joinposter.com/api/auth?application_id={application_id}"
                    f"&redirect_uri={redirect_uri}&response_type=code")

        return redirect(auth_url)


class PosterCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = OAuthCallbackSerializer(data=request.query_params)

        if serializer.is_valid():
            code = serializer.validated_data['code']
            account = serializer.validated_data['account']

            token_url = f"https://{account}.joinposter.com/api/v2/auth/access_token"

            data = {
                'application_id': settings.POSTER_APPLICATION_ID,
                'application_secret': settings.POSTER_APPLICATION_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': settings.POSTER_REDIRECT_URI,
                'code': code
            }

            response = requests.post(token_url, data=data)

            if response.status_code == 200:
                token_data = response.json()

                access_token = token_data.get('access_token')
                account_number = token_data.get('account_number')
                user_data = token_data.get('user', {})
                owner_data = token_data.get('ownerInfo', {})

                venue_exist = Venue.objects.filter(account_number=account_number).exists()
                if venue_exist:
                    logger.info(f"Venue with account number {account_number} already exists.")
                    return Response({'message': 'Venue already exists'}, status=200)

                pos_system = POSSystem.objects.filter(name='Poster').first()
                pos_system_name = pos_system.name.lower()
                pos_service = POSServiceFactory.get_service(pos_system_name, access_token)
                pos_settings = pos_service.get_settings()

                Venue.objects.create(
                    access_token=access_token,
                    account_number=account_number,
                    owner_id=user_data.get('id'),
                    owner_name=user_data.get('name'),
                    owner_email=user_data.get('email'),
                    owner_phone=owner_data.get('phone'),
                    city=owner_data.get('city'),
                    country=owner_data.get('country'),
                    company_name=owner_data.get('company_name'),
                    tip_amount=pos_settings.get('tip_amount'),
                    pos_system=pos_system
                )

                logger.info(f"New venue created with account number {account_number}")

                return Response(
                    {'message': 'Authorization successful', 'access_token': access_token}
                )

            else:
                logger.error(f"Failed to retrieve access token, status code: {response.status_code}")
                return Response({'message': 'Failed to retrieve access token'}, status=response.status_code)
