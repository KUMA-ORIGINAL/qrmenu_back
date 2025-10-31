from modeltranslation.translator import TranslationOptions, register

from ..models import Venue


@register(Venue)
class VenueTranslationOptions(TranslationOptions):
    fields = ('table_qr_text',)
