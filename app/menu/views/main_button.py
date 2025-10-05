from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import MainButton
from ..serializers import MainButtonSerializer


@extend_schema(
    tags=["MainButton"],
    parameters=[
        OpenApiParameter(
            name="venue_slug",
            description="Фильтр по слагу заведения (пример: ?venue_slug=my-cafe)",
            required=True,
            type=str,
        )
    ],
)
class MainButtonsAPIView(APIView):
    """
    Возвращает кнопки главного меню по слагу заведения, разбитые на 2 списка:
    первый — 2 объекта, второй — 3.
    """

    def get(self, request):
        venue_slug = request.query_params.get("venue_slug")
        if not venue_slug:
            return Response(
                {"error": "Параметр 'venue_slug' обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        buttons = MainButton.objects.filter(
            venue__slug__iexact=venue_slug
        ).order_by("order")

        serializer = MainButtonSerializer(buttons, many=True, context={"request": request})
        data = serializer.data

        # группируем (2 + 3)
        grouped = [data[:2], data[2:5]]

        return Response(grouped, status=status.HTTP_200_OK)
