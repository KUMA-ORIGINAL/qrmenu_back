from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from menu.models import Product
from venues.models import Venue
from menu.services import ai_translate_text  # функция перевода через OpenAI


class Command(BaseCommand):
    help = "Переводит названия и описания всех товаров указанного заведения на английский и кыргызский"

    def add_arguments(self, parser):
        parser.add_argument(
            'venue_id',
            type=int,
            help='ID заведения (Venue), для которого нужно перевести товары'
        )

    def handle(self, *args, **options):
        venue_id = options['venue_id']

        try:
            venue = Venue.objects.get(pk=venue_id)
        except Venue.DoesNotExist:
            raise CommandError(f"❌ Заведение с ID={venue_id} не найдено.")

        products = Product.objects.filter(venue=venue)
        if not products.exists():
            self.stdout.write(f"⚠️ У заведения '{venue}' нет товаров для перевода.")
            return

        self.stdout.write(self.style.WARNING(
            f"🔄 Начинаем перевод {products.count()} товаров для заведения: {venue}"
        ))

        updated = 0
        with transaction.atomic():
            for product in products:
                has_changes = False

                # --- Название ---
                if product.product_name:
                    product.product_name_en = ai_translate_text(
                        product.product_name, target_language="en"
                    )
                    product.product_name_ky = ai_translate_text(
                        product.product_name, target_language="ky"
                    )
                    has_changes = True

                # --- Описание ---
                if product.product_description:
                    product.product_description_en = ai_translate_text(
                        product.product_description, target_language="en"
                    )
                    product.product_description_ky = ai_translate_text(
                        product.product_description, target_language="ky"
                    )
                    has_changes = True

                if has_changes:
                    product.save()
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Переведён продукт: {product.product_name}"))

        self.stdout.write(self.style.SUCCESS(
            f"🏁 Готово! Переведено товаров: {updated} из {products.count()}"
        ))
