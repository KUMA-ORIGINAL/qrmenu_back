from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from phonenumber_field.phonenumber import to_python

from venues.models import Venue
from orders.models import Client, ClientVenueProfile
from orders.api.v1.serializers import ClientBonusSerializer


@extend_schema(tags=['Client'])
class ClientBonusAPIView(APIView):

    @extend_schema(
        summary="Получить бонусы клиента по номеру телефона",
        description="Возвращает бонусы клиента по конкретному заведению.",
        parameters=[
            OpenApiParameter(
                name="phone",
                description="Номер телефона клиента (например: +996500123456)",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='venue_slug',
                description='Слаг заведения',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiExample(
                "Успех",
                value={"phone": "+996500123456", "venue": "coffee-house", "bonus": 150},
                response_only=True,
                status_codes=[200],
            ),
            400: OpenApiExample(
                "Некорректный запрос",
                value={"error": "Укажите номер телефона в параметре phone"},
                response_only=True,
                status_codes=[400],
            ),
            404: OpenApiExample(
                "Клиент не найден",
                value={"error": "Клиент не найден"},
                response_only=True,
                status_codes=[404],
            ),
        },
    )
    def get(self, request):
        venue_slug = request.query_params.get('venue_slug')
        phone = request.query_params.get("phone")

        if not venue_slug:
            return Response({'error': 'venue_slug is required.'}, status=status.HTTP_400_BAD_REQUEST)

        venue = Venue.objects.filter(slug=venue_slug.lower()).first()
        if not venue:
            return Response({'error': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not phone:
            return Response({"error": "Укажите номер телефона в параметре phone"},
                            status=status.HTTP_400_BAD_REQUEST)

        normalized_phone = to_python(phone)
        if not normalized_phone:
            return Response({"error": "Некорректный номер телефона"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(phone_number=normalized_phone)
        except Client.DoesNotExist:
            return Response({"error": "Клиент не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        profile = ClientVenueProfile.objects.filter(client=client, venue=venue).first()
        bonus = profile.bonus if profile else 0

        data = {
            "phone_number": client.phone_number,
            "venue": venue.slug,
            "bonus": bonus,
        }
        serializer = ClientBonusSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
