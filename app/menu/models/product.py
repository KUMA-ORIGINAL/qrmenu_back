from django.db import models


class Product(models.Model):
    external_id = models.CharField(max_length=100, verbose_name="Внешний ID товара")
    product_name = models.CharField(max_length=255, verbose_name="Название товара")
    product_description = models.TextField(blank=True, null=True, verbose_name="Описание товара")
    product_photo = models.ImageField(upload_to='menu/products/%Y/%m', blank=True, null=True,
                                      verbose_name="Фото товара")
    product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0, verbose_name="Цена товара")
    hidden = models.BooleanField(default=False, verbose_name="Скрытый товар")

    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    venue = models.ForeignKey('account.Venue', on_delete=models.CASCADE, related_name='products', verbose_name="Заведение")
    pos_system = models.ForeignKey('account.POSSystem', on_delete=models.CASCADE, verbose_name="POS система")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['product_name']

    def __str__(self):
        return self.product_name
