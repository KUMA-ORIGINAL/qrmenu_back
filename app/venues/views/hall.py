from django.http import JsonResponse

from venues.models import Hall


def get_halls_by_spot(request):
    spot_id = request.GET.get('spot_id')
    halls = Hall.objects.filter(spot_id=spot_id).values('id', 'hall_name')
    return JsonResponse(list(halls), safe=False)
