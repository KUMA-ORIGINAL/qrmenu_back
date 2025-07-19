import logging
import json

from import_export import resources, fields, widgets

from .models import Product, Modificator

logger = logging.getLogger(__name__)


class ProductResource(resources.ModelResource):

    def __init__(self, *args, context=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = context or {}

    class Meta:
        model = Product
        import_id_fields = ('product_name',)  # Используем product_name как уникальный идентификатор
        fields = (
            'product_name', 'product_description',
            'product_price', 'weight', 'is_recommended', 'hidden',
            'modificators',
        )

    def after_save_instance(self, instance, using_transactions, dry_run, **kwargs):
        # row - это словарь текущей строки (в json - это dict)
        row = getattr(self, 'current_row', None)

        # Не создавать модификаторы в режиме dry_run (превью)
        if dry_run:
            logger.info("Dry run mode - skipping modificator creation")
            return

        if row:
            logger.info(f"Processing row for instance {instance.id}: {row}")

            # Удаляем старые модификаторы перед созданием новых
            if instance.pk:
                Modificator.objects.filter(product=instance).delete()
                logger.info(f"Deleted existing modificators for product {instance.id}")

            modificators_data = row.get('modificators')
            if modificators_data:
                logger.info(f"Found modificators data: {modificators_data}")

                # Если modificators - это строка JSON, парсим её
                if isinstance(modificators_data, str):
                    try:
                        modificators_data = json.loads(modificators_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse modificators JSON: {e}")
                        return

                # Если modificators - это список
                if isinstance(modificators_data, list):
                    for mod in modificators_data:
                        logger.info(f"Creating modificator: {mod}")
                        try:
                            Modificator.objects.create(
                                product=instance,
                                name=mod.get('name'),
                                price=mod.get('price', 0),
                            )
                            logger.info(f"Successfully created modificator: {mod.get('name')}")
                        except Exception as e:
                            logger.error(f"Failed to create modificator {mod}: {e}")
                else:
                    logger.warning(f"Modificators data is not a list: {type(modificators_data)}")
            else:
                logger.info("No modificators data found in row")

    def import_row(self, row, instance_loader, **kwargs):
        # сохраняем текущую строку для after_save_instance
        self.current_row = row
        logger.info(f"Importing row: {row}")
        return super().import_row(row, instance_loader, **kwargs)

    def skip_row(self, instance, original, row, import_validation_errors=None):
        # Не пропускать строки, даже если продукт существует
        # Это нужно для обновления модификаторов
        logger.info(f"Checking if should skip row for product: {getattr(instance, 'product_name', 'Unknown')}")
        return False

    def before_save_instance(self, instance, using_transactions, dry_run, **kwargs):
        logger.info(f"Before save instance: {instance.product_name}, dry_run: {dry_run}")

        if self.context.get('venue_id'):
            instance.venue_id = self.context['venue_id'].pk if hasattr(self.context['venue_id'], 'pk') else \
                self.context['venue_id']
        if self.context.get('spot_id'):
            instance.spot_id = self.context['spot_id'].pk if hasattr(self.context['spot_id'], 'pk') else self.context[
                'spot_id']
        if self.context.get('category_id'):
            instance.category_id = self.context['category_id'].pk if hasattr(self.context['category_id'], 'pk') else \
                self.context['category_id']