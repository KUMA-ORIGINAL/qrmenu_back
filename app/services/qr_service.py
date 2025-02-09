from io import BytesIO

import qrcode
from django.conf import settings
from django.templatetags.static import static
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def generate_qr_with_logo(data, logo_path, box_size=10, border=4):
    """Генерация QR-кода с улучшенным логотипом."""
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Генерация изображения QR-кода с уменьшенным логотипом
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        embeded_image_path=logo_path,
        module_drawer=RoundedModuleDrawer(),
    )

    return qr_img


def pil_image_to_bytes(image):
    """Convert PIL Image to BytesIO buffer for use in ReportLab."""
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


def create_pdf_with_qr(output_pdf_path, data1, data2, logo_path, text_top1, text_bottom1, text_top2, text_bottom2):
    width, height = landscape(A4)

    c = canvas.Canvas(output_pdf_path, pagesize=landscape(A4))

    pdfmetrics.registerFont(TTFont('Roboto', 'static/Roboto.ttf'))

    qr_size = 300  # Размер QR-кода
    qr1_img = generate_qr_with_logo(data1, logo_path, box_size=10)
    qr2_img = generate_qr_with_logo(data2, logo_path, box_size=10)

    # Преобразуем изображения в буфер BytesIO для использования в ReportLab
    qr1_img_buffer = pil_image_to_bytes(qr1_img)
    qr2_img_buffer = pil_image_to_bytes(qr2_img)

    margin = ((width / 2 - 330) / 4) * mm
    qr_y = height / 2 - qr_size / 2
    line_x = width / 2
    qr1_x = margin
    qr2_x = width - qr_size - margin

    c.setFont("Roboto", 20)

    c.drawString(qr1_x + 60, qr_y + qr_size + 20, text_top1)
    c.drawString(qr1_x + 60, qr_y - 30, text_bottom1)
    c.drawString(qr2_x + 60, qr_y + qr_size + 20, text_top2)
    c.drawString(qr2_x + 60, qr_y - 30, text_bottom2)

    # Используем ImageReader для рендеринга изображений в PDF
    c.drawImage(ImageReader(qr1_img_buffer), qr1_x, qr_y, width=qr_size, height=qr_size)
    c.drawImage(ImageReader(qr2_img_buffer), qr2_x, qr_y, width=qr_size, height=qr_size)

    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.line(line_x, 0, line_x, height)

    c.showPage()
    c.save()
