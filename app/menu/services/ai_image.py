import openai
import base64
from django.core.files.base import ContentFile
from django.conf import settings


openai.api_key = settings.OPENAI_API_KEY


def ai_improve_image(instance, field_name='image', prompt=None):
    image_field = getattr(instance, field_name, None)
    if not image_field:
        return "❌ Нет изображения"

    if not image_field.path:
        return "⚠️ Файл не сохранён на диске"

    image_path = image_field.path

    base_prompt = f"Improve the image quality for {instance.__class__.__name__.lower()} '{instance}'."

    if prompt:
        full_prompt = f"{prompt.strip()} (for {instance.__class__.__name__.lower()} '{instance}')"
    else:
        full_prompt = base_prompt

    with open(image_path, "rb") as img_file:
        result = openai.images.edit(
            model="gpt-image-1",
            image=img_file,
            prompt=full_prompt,
            size="1024x1024"
        )

    img_data = base64.b64decode(result.data[0].b64_json)
    file_name = f"{instance.__class__.__name__.lower()}_{instance.pk}_improved.png"
    image_field.save(file_name, ContentFile(img_data))
    instance.save()

    return f"✅ Изображение улучшено ({file_name})"


def ai_generate_image(instance, field_name='image', prompt=None):
    base_prompt = f"Generate a professional photo for {instance.__class__.__name__.lower()} '{instance}'."

    if prompt:
        full_prompt = f"{prompt.strip()} (for {instance.__class__.__name__.lower()} '{instance}')"
    else:
        full_prompt = base_prompt

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
