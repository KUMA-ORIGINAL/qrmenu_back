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

def create_overlay_pdf(qr_image_buffer, x1, y1, x2, y2, width, height,
                       text_top1, text_top2, is_table):
    text_bottom1_ru = "Ваш персональный\nонлайн-официант"
    text_bottom1_kg = "Сиздин жеке\nонлайн-официантыңыз"
    text_bottom2_ru = ("Заказывайте еду и напитки онлайн с доставкой\n"
                       "прямо к вашему столу! Просто отсканируйте QR-код")
    text_bottom2_kg = ("Тамак-аш менен суусундуктарга онлайн буюртма бериңиз —\n"
                       "түз эле дасторконуңузга жеткирип беришет!\n"
                       "Болгону QR-кодду сканерлеңиз.")

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))

    pdfmetrics.registerFont(TTFont('Inter', 'static/Inter_18pt-Bold.ttf'))

    line_spacing = 20  # Расстояние между строками для основного текста

    # Центры QR-блоков
    center_x1 = x1 + width / 2
    center_x2 = x2 + width / 2

    # --- Верхний текст (белый на розовом фоне) ---
    can.setFont('Inter', 36)
    can.setFillColor(HexColor("#FFFFFF"))
    can.drawCentredString(center_x1, y1 + height + 20, text_top1)

    if is_table:
        can.drawCentredString(center_x2, y1 + height + 20, text_top2)
    else:
        kg_text_top2_lines = text_top2.split('\n')
        y_offset_kg_text_top2 = y1 + height + 45

        for line in kg_text_top2_lines:
            can.drawCentredString(center_x2, y_offset_kg_text_top2, line)
            y_offset_kg_text_top2 -= 30

    # --- QR-коды ---
    qr_image = ImageReader(qr_image_buffer)
    can.drawImage(qr_image, x1, y1, width=width, height=height)
    can.drawImage(qr_image, x2, y2, width=width, height=height)

    # --- ЛЕВАЯ ЧАСТЬ (Русский) ---
    # Заголовок на русском (черный текст)
    can.setFillColor(HexColor("#000000"))
    can.setFont('Inter', 14)

    # Разбиваем текст на строки для text_bottom1_ru
    ru_title_lines = text_bottom1_ru.split('\n')
    y_offset_ru_title = y1 - 150

    for line in ru_title_lines:
        can.drawCentredString(center_x1, y_offset_ru_title, line)
        y_offset_ru_title -= 15

    # Основной текст на русском (серый)
    can.setFillColor(HexColor("#939393"))
    can.setFont('Inter', 14)

    # Разбиваем текст на строки для нижнего текста (русский)
    ru_lines = text_bottom2_ru.split('\n')
    y_offset_ru = y1 - 220

    for line in ru_lines:
        can.drawCentredString(center_x1, y_offset_ru, line)
        y_offset_ru -= line_spacing

    # --- ПРАВАЯ ЧАСТЬ (Киргизский) ---
    # Заголовок на киргизском (черный текст)
    can.setFillColor(HexColor("#000000"))
    can.setFont('Inter', 14)

    # Разбиваем текст на строки для text_bottom1_kg
    kg_title_lines = text_bottom1_kg.split('\n')
    y_offset_kg_title = y2 - 150

    for line in kg_title_lines:
        can.drawCentredString(center_x2, y_offset_kg_title, line)
        y_offset_kg_title -= 15

    # Основной текст на киргизском (серый)
    can.setFillColor(HexColor("#939393"))
    can.setFont('Inter', 12)

    # Разбиваем текст на строки для нижнего текста (киргизский)
    kg_lines = text_bottom2_kg.split('\n')
    y_offset_kg = y2 - 220

    for line in kg_lines:
        can.drawCentredString(center_x2, y_offset_kg, line)
        y_offset_kg -= line_spacing

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

def add_qr_and_text_to_pdf_in_memory(qr_url, text_top1, text_top2, is_table=False):
    """Добавляет QR-коды и текст в PDF, используя миллиметры для координат."""
    qr_image_path = create_qr_code_in_memory(qr_url)
    input_pdf = "static/input_pdf_for_qr.pdf"

    qr_width = 70 * mm
    qr_height = 70 * mm
    x1 = 39 * mm
    y1 = 100 * mm
    x2 = x1 * 3 + qr_height + 1 * mm
    y2 = 100 * mm

    overlay_pdf = create_overlay_pdf(
        qr_image_path, x1, y1, x2, y2, qr_width, qr_height,
        text_top1, text_top2, is_table
    )
    return merge_pdf_with_overlay(input_pdf, overlay_pdf)
