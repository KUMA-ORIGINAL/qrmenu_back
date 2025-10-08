from django.http import JsonResponse
from venues.models import Spot


def get_spots(request):
    venue_id = request.GET.get('venue_id')
    spots = Spot.objects.filter(venue_id=venue_id).values('id', 'name')
    return JsonResponse(list(spots), safe=False)
