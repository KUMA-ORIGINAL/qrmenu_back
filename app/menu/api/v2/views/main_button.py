from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from menu.models import MainButton
from menu.api.v2.serializers import MainButtonSerializer


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

        cache_key = f"main_buttons:{venue_slug.lower()}"
        data = cache.get(cache_key)

        # if not data:
        buttons = (
            MainButton.objects
            .filter(venue__slug__iexact=venue_slug)
            .select_related("section", "category", "venue")
            .prefetch_related("section__categories")
            .order_by("order")
        )

        serializer = MainButtonSerializer(buttons, many=True, context={"request": request})
        serialized_data = serializer.data

        # группировка (2 + 3)
        grouped = [serialized_data[:2], serialized_data[2:5]]

        cache.set(cache_key, grouped, 60 * 30)  # 30 минут
        data = grouped

        return Response(data, status=status.HTTP_200_OK)
