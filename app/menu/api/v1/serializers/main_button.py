from rest_framework import serializers
from menu.models import MainButton


class MainButtonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = MainButton
        fields = [
            "id",
            "button_type",
            "order",
            "name",
            "photo",
        ]

    def get_name(self, obj):
        """
        Возвращает имя из связанного раздела или категории.
        """
        if obj.section:
            return getattr(obj.section, "name", None)
        if obj.category:
            return getattr(obj.category, "category_name", None)
        return None

    def get_photo(self, obj):
        """
        Возвращает url картинки из section/category, если есть поле photo/photo.
        """
        photo_field = None

        # Проверяем Section
        if obj.section:
            photo_field = getattr(obj.section, "photo_small", None)

        if not photo_field and obj.category:
            photo_field = getattr(obj.category, "category_photo_small", None)

        if not photo_field:
            return None

        request = self.context.get("request")
        url = getattr(photo_field, "url", None) if hasattr(photo_field, "url") else str(photo_field)

        if url and request and not url.startswith("http"):
            url = request.build_absolute_uri(url)

        return url
