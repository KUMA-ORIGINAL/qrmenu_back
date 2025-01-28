from django.db import models

from services.model import BaseModel


class POSSystem(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
