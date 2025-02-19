from modeltranslation.translator import TranslationOptions, register

from ..models import Modificator


@register(Modificator)
class ModificatorTranslationOptions(TranslationOptions):
    fields = ('name', )