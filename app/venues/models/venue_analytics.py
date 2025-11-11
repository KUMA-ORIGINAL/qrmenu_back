from django.db import models


class VenueAnalytics(models.Model):
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='analytics')
    table = models.ForeignKey('venues.Table', null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(auto_now_add=True)
    unique_visitors = models.JSONField(default=list, blank=True)  # список ID уникальных клиентов
    unique_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('venue', 'table', 'date')

    def register_visit(self, client_id: str):
        """Добавляем клиента в список, если он ещё не засчитан."""
        if client_id and client_id not in self.unique_visitors:
            self.unique_visitors.append(client_id)
            self.unique_count = len(self.unique_visitors)
            self.save(update_fields=['unique_visitors', 'unique_count'])
