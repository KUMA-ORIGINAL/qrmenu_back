from django.utils.safestring import mark_safe
from unfold.widgets import UnfoldAdminFileFieldWidget


class AiPhotoWidget(UnfoldAdminFileFieldWidget):
    """Виджет для поля category_photo с кнопкой AI."""

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)

        # Определяем, есть ли уже фото
        has_photo = bool(value and hasattr(value, "url"))

        if has_photo:
            button_text = "Улучшить AI"
            button_action = "aiImprove(this)"
        else:
            button_text = "Сгенерировать AI"
            button_action = "aiGenerate(this)"

        button_classes = (
            "font-medium flex group items-center gap-2 px-2 py-1 rounded-default "
            "justify-center whitespace-nowrap cursor-pointer border border-base-200 "
            "bg-primary-600 border-transparent text-white mt-2"
        )

        button_html = (
            f'<button type="button" class="{button_classes}" onclick="{button_action}">{button_text}</button>'
        )

        return mark_safe(f"<div>{input_html}{button_html}</div>")
