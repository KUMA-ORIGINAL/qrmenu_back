from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from phonenumber_field.phonenumber import to_python

from ..models import Client
from ..serializers import ClientBonusSerializer


@extend_schema(
    tags=['Client'],
)
class ClientBonusAPIView(APIView):

    @extend_schema(
        summary="Получить бонусы клиента по номеру телефона",
        description="Принимает номер телефона клиента и возвращает количество бонусов.",
        parameters=[
            OpenApiParameter(
                name="phone",
                description="Номер телефона клиента (например: +996500123456)",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            )
        ],
        responses={
            200: ClientBonusSerializer,
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
        phone = request.query_params.get("phone")

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

        serializer = ClientBonusSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)
