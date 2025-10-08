from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from tg_bot.utils import notify_waiter
from venues.models import Table


@extend_schema(tags=['Call Waiter'])
class CallWaiterView(APIView):
    @extend_schema(
        summary="Вызов официанта",
        description="Эндпоинт для вызова официанта по ID стола. Table ID передаётся через query-параметр.",
        parameters=[
            OpenApiParameter(
                name="table_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID стола"
            )
        ],
        responses={
            200: OpenApiExample("Успешный вызов официанта", value={"status": "ok"}),
            404: OpenApiExample("Стол не найден", value={"error": "Table not found"}),
        },
    )
    def get(self, request, *args, **kwargs):
        """Вызов официанта по query параметру ?table_id=..."""
        table_id = request.query_params.get("table_id")

        if not table_id:
            return Response(
                {"error": "table_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)

        notify_waiter(table)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
