import uuid

from django.db import models


class PhoneVerification(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    hash = models.CharField(max_length=64, null=True, blank=True, unique=True)
    is_bonus_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone} - {self.code}"

    def generate_hash(self):
        """Генерация хэша при подтверждении кода"""
        if not self.hash:
            self.hash = uuid.uuid4().hex
        self.is_verified = True
        self.is_bonus_verified = True
        self.save()
        return self.hash
