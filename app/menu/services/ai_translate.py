import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY


def ai_translate_text(text: str, target_language: str = "en") -> str:
    """
    Переводит текст на заданный язык с помощью OpenAI GPT.
    Возвращает только переведённый текст без лишних пояснений.
    """

    text = text.strip()
    if not text:
        return ""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # можно заменить на "gpt-4o"
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translation engine. "
                    "Translate the user's text into the requested language. "
                    "Return only the translated text without any explanations, comments, or quotes."
                ),
            },
            {
                "role": "user",
                "content": f"Language: {target_language}\nText: {text}",
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
