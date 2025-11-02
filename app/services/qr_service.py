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

def draw_wrapped_two_lines_text(can, text, center_x, y, max_width, max_height,
                                font_name="Inter", font_size=32, min_font_size=22,
                                line_spacing=1.2, color="#FFFFFF"):
    """
    Рисует текст по центру, разбивая ровно на 2 строки и
    автоматически уменьшая шрифт, чтобы вписать текст в заданные размеры.
    """
    can.setFillColor(HexColor(color))

    def split_into_two_lines(size):
        """Разбивает текст примерно пополам, стараясь чтобы обе строки влезли по ширине."""
        words = text.split()
        if not words:
            return ["", ""]
        # Наращиваем первую строку, пока она помещается
        line1, line2 = "", ""
        for word in words:
            test_line = f"{line1} {word}".strip()
            if can.stringWidth(test_line, font_name, size) <= max_width:
                line1 = test_line
            else:
                # Остаток идёт во вторую строку
                remaining = words[words.index(word):]
                line2 = " ".join(remaining)
                break
        else:
            line2 = ""  # всё влезло в одну строку
        return [line1, line2]

    while font_size >= min_font_size:
        lines = split_into_two_lines(font_size)
        # Проверяем ширину для обеих строк
        if all(can.stringWidth(line, font_name, font_size) <= max_width for line in lines):
            total_height = (len(lines) - 1) * font_size * line_spacing
            if total_height <= max_height:
                break
        font_size -= 1

    can.setFont(font_name, font_size)
    total_height = (len(lines) - 1) * font_size * line_spacing
    start_y = y + total_height / 2

    for i, line in enumerate(lines):
        line_y = start_y - i * font_size * line_spacing
        can.drawCentredString(center_x, line_y, line)


def create_overlay_pdf(qr_image_buffer, x1, y1, x2, y2, width, height,
                       text_top1, text_top2, table_num, is_table):
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
            draw_wrapped_two_lines_text(
                can, text_top1, center_x1, y1 + height + 45, max_text_width,
                max_height=text_zone_height, font_name=font_name)
            draw_wrapped_two_lines_text(
                can, text_top2, center_x2, y1 + height + 45, max_text_width,
                max_height=text_zone_height, font_name=font_name)

        can.setFont('Inter', 18)
        can.setFillColor(HexColor("#000000"))
        if table_num:
            can.drawCentredString(center_x1, 40, f"Стол {table_num}")
            can.drawCentredString(center_x2, 40, f"Стол {table_num}")
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


def add_qr_and_text_to_pdf_in_memory(qr_url, text_top1, text_top2, table_num, input_pdf_color, is_table=False):
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
        text_top1, text_top2, table_num, is_table
    )
    return merge_pdf_with_overlay(input_pdf, overlay_pdf)
