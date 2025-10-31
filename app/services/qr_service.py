from textwrap import wrap

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
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    return qr_buffer


def draw_wrapped_autosize_text(can, text, center_x, y, max_width,
                                max_height,  # высота зоны, куда хотим вписать текст
                                font_name="Inter", font_size=34,
                                min_font_size=26,
                                line_spacing=1.2, color="#FFFFFF"):
    """
    Рисует текст по центру с автоматическим уменьшением шрифта,
    если блок выходит за пределы max_height.
    """
    can.setFillColor(HexColor(color))

    def build_lines(size):
        """Разбивает текст на строки по ширине с заданным шрифтом."""
        words = text.split()
        lines, current_line = [], ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if can.stringWidth(test_line, font_name, size) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    # Пробуем уменьшать текст, пока он не впишется в отведённую область
    lines = build_lines(font_size)
    while font_size > min_font_size:
        total_height = (len(lines) - 1) * font_size * line_spacing
        if total_height <= max_height:
            break
        font_size -= 1
        lines = build_lines(font_size)

    # После подбора размера — выставляем шрифт и центрируем блок
    can.setFont(font_name, font_size)
    total_height = (len(lines) - 1) * font_size * line_spacing
    start_y = y + total_height / 2  # лёгкое выравнивание вверх

    for i, line in enumerate(lines):
        line_y = start_y - i * font_size * line_spacing
        can.drawCentredString(center_x, line_y, line)


def create_overlay_pdf(qr_image_buffer, x1, y1, x2, y2, width, height,
                       text_top1, text_top2, is_table):
    text_bottom1_ru = "Ваш персональный\nонлайн-официант"
    text_bottom1_kg = "Сиздин жеке\nонлайн-официантыңыз"

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))

    pdfmetrics.registerFont(TTFont('Inter', 'static/Inter_18pt-Bold.ttf'))

    # Центры QR-блоков
    center_x1 = x1 + width / 2
    center_x2 = x2 + width / 2

    # --- Верхний текст (белый на розовом фоне) ---
    can.setFont('Inter', 36)
    can.setFillColor(HexColor("#FFFFFF"))
    font_name = "Inter"
    max_text_width = 350
    text_zone_height = 40

    if is_table:
        if any(ch.isdigit() for ch in text_top1):
            can.drawCentredString(center_x1, y1 + height + 20, text_top1)
            can.drawCentredString(center_x2, y1 + height + 20, text_top2)
        else:
            draw_wrapped_autosize_text(
                can, text_top1, center_x1, y1 + height + 45, max_text_width,
                max_height=text_zone_height, font_name=font_name)
            draw_wrapped_autosize_text(
                can, text_top2, center_x2, y1 + height + 45, max_text_width,
                max_height=text_zone_height, font_name=font_name)
    else:
        can.drawCentredString(center_x1, y1 + height + 20, text_top1)
        kg_text_top2_lines = text_top2.split('\n')
        y_offset_kg_text_top2 = y1 + height + 45

        for line in kg_text_top2_lines:
            can.drawCentredString(center_x2, y_offset_kg_text_top2, line)
            y_offset_kg_text_top2 -= 30

    # --- QR-коды ---
    qr_image = ImageReader(qr_image_buffer)
    can.drawImage(qr_image, x1, y1, width=width, height=height)
    can.drawImage(qr_image, x2, y2, width=width, height=height)

    # --- Новый текст: NFC подсказка ---
    can.setFont('Inter', 16)
    can.setFillColor(HexColor("#FFFFFF"))  # красный цвет как в примере

    text_indent = -10  # насколько сдвинуть текст влево (можно регулировать)

    # Под левым QR (русский текст в 3 строки)
    nfc_text_ru_lines = "Прислоните\nсмартфон к\nNFC".split('\n')
    y_offset_nfc_ru = y1 - 40
    for line in nfc_text_ru_lines:
        can.drawString(center_x1 + text_indent, y_offset_nfc_ru, line)
        y_offset_nfc_ru -= 18  # шаг между строками

    # Под правым QR (кыргызский текст в 3 строки)
    nfc_text_kg_lines = "NFCке\nсмартфонду\nжакындатыңыз".split('\n')
    y_offset_nfc_kg = y2 - 40
    for line in nfc_text_kg_lines:
        can.drawString(center_x2 + text_indent, y_offset_nfc_kg, line)
        y_offset_nfc_kg -= 18

    # --- ЛЕВАЯ ЧАСТЬ (Русский) ---
    # Заголовок на русском (черный текст)
    can.setFillColor(HexColor("#000000"))
    can.setFont('Inter', 14)

    # Разбиваем текст на строки для text_bottom1_ru
    ru_title_lines = text_bottom1_ru.split('\n')
    y_offset_ru_title = y1 - 215

    for line in ru_title_lines:
        can.drawCentredString(center_x1, y_offset_ru_title, line)
        y_offset_ru_title -= 15

    # Основной текст на русском (серый)
    can.setFillColor(HexColor("#939393"))
    can.setFont('Inter', 14)

    # --- ПРАВАЯ ЧАСТЬ (Киргизский) ---
    # Заголовок на киргизском (черный текст)
    can.setFillColor(HexColor("#000000"))
    can.setFont('Inter', 14)

    # Разбиваем текст на строки для text_bottom1_kg
    kg_title_lines = text_bottom1_kg.split('\n')
    y_offset_kg_title = y2 - 215

    for line in kg_title_lines:
        can.drawCentredString(center_x2, y_offset_kg_title, line)
        y_offset_kg_title -= 15

    # Основной текст на киргизском (серый)
    can.setFillColor(HexColor("#939393"))
    can.setFont('Inter', 12)

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


def add_qr_and_text_to_pdf_in_memory(qr_url, text_top1, text_top2, input_pdf_color, is_table=False):
    """Добавляет QR-коды и текст в PDF, используя миллиметры для координат."""
    qr_image_path = create_qr_code_in_memory(qr_url)
    input_pdf = f"static/input_pdfs/{input_pdf_color}.pdf"

    qr_width = 66 * mm
    qr_height = 66 * mm
    x1 = 40 * mm
    y1 = 107 * mm
    x2 = x1 * 3 + qr_height + 3 * mm
    y2 = 107 * mm

    overlay_pdf = create_overlay_pdf(
        qr_image_path, x1, y1, x2, y2, qr_width, qr_height,
        text_top1, text_top2, is_table
    )
    return merge_pdf_with_overlay(input_pdf, overlay_pdf)
