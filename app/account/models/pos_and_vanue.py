from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class POSSystem(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=255)
    pos_system = models.ForeignKey(POSSystem, on_delete=models.CASCADE)
    api_token = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # Владелец заведения (пользователь)

    def __str__(self):
        return self.name
