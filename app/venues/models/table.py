from django.db import models


class Table(models.Model):
    external_id = models.CharField(max_length=100, verbose_name="Внешний ID стола")
    table_num = models.CharField(max_length=255)
    table_title = models.CharField(max_length=255)
    spot_id = models.IntegerField()
    table_shape = models.CharField(max_length=50,
                                   choices=[('square', 'Square'), ('circle', 'Circle')])
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='tables')


    def __str__(self):
        return f"Table {self.table_num} ({self.table_title})"
