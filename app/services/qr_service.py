from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
from PyPDF2 import PdfReader, PdfWriter


def create_qr_code_in_memory(url):
    """Создает QR-код и возвращает его в виде BytesIO."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    return qr_buffer

def create_overlay_pdf(qr_image_buffer, x1, y1, x2, y2, width, height, text_top):
    """Создает PDF-слой с QR-кодами и центрированным текстом в памяти."""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))

    font_name = 'Inter'
    font_size = 40
    pdfmetrics.registerFont(TTFont(font_name, 'static/Inter_18pt-Bold.ttf'))
    can.setFont(font_name, font_size)
    can.setFillColor(HexColor("#FFFFFF"))

    # Получаем ширину текста
    text_width = stringWidth(text_top, font_name, font_size)

    # Центрируем текст над каждым QR-кодом
    text_x1 = x1 + (width - text_width) / 2
    text_x2 = x2 + (width - text_width) / 2
    text_y = y1 + height + 20  # Y-координата текста

    # Рисуем текст
    can.drawString(text_x1, text_y, text_top)
    can.drawString(text_x2, text_y, text_top)

    # Конвертируем BytesIO в ImageReader
    qr_image = ImageReader(qr_image_buffer)

    # Добавляем QR-коды
    can.drawImage(qr_image, x1, y1, width=width, height=height)
    can.drawImage(qr_image, x2, y2, width=width, height=height)

    can.save()
    packet.seek(0)
    return PdfReader(packet)

def merge_pdf_with_overlay(input_pdf_stream, overlay_pdf):
    """Объединяет существующий PDF с наложением и возвращает итоговый PDF в виде BytesIO."""
    reader = PdfReader(input_pdf_stream)
    writer = PdfWriter()

    # Добавляем QR-код и текст на каждую страницу существующего PDF
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    output_pdf_stream = BytesIO()
    writer.write(output_pdf_stream)
    output_pdf_stream.seek(0)
    return output_pdf_stream

def add_qr_and_text_to_pdf_in_memory(qr_url, text_top):
    """Добавляет QR-коды и текст в PDF, используя миллиметры для координат."""
    qr_image_path = create_qr_code_in_memory(qr_url)
    input_pdf = "static/input_pdf_for_qr.pdf"

    qr_width = 70 * mm
    qr_height = 70 * mm
    x1 = 39 * mm
    y1 = 100 * mm
    x2 = x1 * 3 + qr_height + 1 * mm
    y2 = 100 * mm

    overlay_pdf = create_overlay_pdf(qr_image_path, x1, y1, x2, y2, qr_width, qr_height, text_top)
    return merge_pdf_with_overlay(input_pdf, overlay_pdf)

