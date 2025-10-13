import openai
import base64
from django.core.files.base import ContentFile
from django.conf import settings


openai.api_key = settings.OPENAI_API_KEY


def ai_improve_image(instance, field_name='image', prompt=None):
    """
    Улучшает существующее изображение модели через AI.
    """
    image_field = getattr(instance, field_name, None)
    if not image_field:
        return "❌ Нет изображения"

    if not image_field.path:
        return "⚠️ Файл не сохранён на диске"

    # путь к реальному файлу
    image_path = image_field.path

    base_prompt = f"Improve the image quality for {instance.__class__.__name__.lower()} '{instance}'."
    full_prompt = prompt or base_prompt

    # Передаём ОТКРЫТЫЙ файл как file-like object
    with open(image_path, "rb") as img_file:
        result = openai.images.edit(
            model="gpt-image-1",
            image=img_file,                # именно файл, не bytes
            prompt=full_prompt,
            size="1024x1024"
        )

    img_data = base64.b64decode(result.data[0].b64_json)
    file_name = f"{instance.__class__.__name__.lower()}_{instance.pk}_improved.png"
    image_field.save(file_name, ContentFile(img_data))
    instance.save()

    return f"✅ Изображение улучшено ({file_name})"


def ai_generate_image(instance, field_name='image', prompt=None):
    """
    Генерация новой картинки по описанию экземпляра.
    """
    base_prompt = f"Generate a professional photo for {instance.__class__.__name__.lower()} '{instance}'."
    full_prompt = prompt or base_prompt

    result = openai.images.generate(
        model="gpt-image-1",
        prompt=full_prompt,
        size="1024x1024"
    )

    img_data = base64.b64decode(result.data[0].b64_json)
    file_name = f"{instance.__class__.__name__.lower()}_{instance.pk}_generated.png"
    image_field = getattr(instance, field_name, None)
    image_field.save(file_name, ContentFile(img_data))
    instance.save()
    return f"✅ Новое изображение сгенерировано ({file_name})"
