# utils/helpers.py
import pygame
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt


def wrap_text(text, width_chars):
    """
    Simple word-wrap function returning list of lines.
    Adjust as needed if you have a more sophisticated version.
    """
    words = text.split()
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        word_len = len(word)
        if current_len + word_len + len(current_line) > width_chars:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_len = word_len
        else:
            current_line.append(word)
            current_len += word_len + 1  # +1 for space

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def render_wrapped_text(surface, wrapped_lines, font, x, y, color=(255, 255, 255, 255)):
    """
    Renders wrapped text lines onto a pygame surface.
    Debug version with visibility enforcement and logging.
    """
    print("[DEBUG render_wrapped_text] Starting render")
    print(f"    Surface size: {surface.get_size()}")
    print(f"    Lines to render: {len(wrapped_lines)}")
    print(f"    Color requested: {color}")

    # Force visible background so Qt doesn't discard transparent surface
    surface.fill((20, 20, 30))  # dark gray-blue — visible even if text fails
    print("[DEBUG] Surface filled with dark background")

    # Safety check: if color has alpha=0 → force opaque white
    if len(color) == 4 and color[3] == 0:
        color = (255, 255, 255, 255)
        print("[DEBUG] Alpha was 0 → forced opaque white")

    # Fallback: force bright red if text still invisible
    if color[:3] == (0, 0, 0) or color[:3] == (255, 255, 255):  # black or white → suspect
        color = (255, 0, 0, 255)  # bright red — impossible to miss
        print("[DEBUG] Forced bright red text for visibility test")

    current_y = y
    line_height = font.get_linesize()

    for line in wrapped_lines:
        if not line.strip():
            current_y += line_height
            continue

        try:
            text_surf = font.render(line, True, color[:3], None)  # True = antialias
            text_rect = text_surf.get_rect(topleft=(x, current_y))
            
            print(f"[DEBUG] Rendering line: '{line}' at y={current_y}")
            print(f"    Text surface size: {text_surf.get_size()}")
            
            surface.blit(text_surf, text_rect)
            print(f"[DEBUG] Blitted line at ({x}, {current_y})")
            
            current_y += line_height
        except Exception as e:
            print(f"[ERROR in render_wrapped_text] Failed to render line '{line}': {e}")

    print("[DEBUG render_wrapped_text] Render complete")
    return surface


def pygame_surf_to_pixmap(surface):
    """Robust Pygame → QPixmap conversion with forced visibility + debug"""
    if surface is None or surface.get_width() == 0 or surface.get_height() == 0:
        print("[ERROR] Invalid surface - returning empty pixmap")
        return QPixmap()

    w, h = surface.get_size()
    print(f"[DEBUG pixmap] Surface size: {w}x{h}")

    # Get bytes in BGRA (Windows/Qt native order)
    data = pygame.image.tostring(surface, 'BGRA', False)  # BGRA, no flip

    # Create QImage with BGRA format
    qimg = QImage(data, w, h, QImage.Format_ARGB32)

    if qimg.isNull():
        print("[ERROR] QImage creation failed (null)")
        return QPixmap()

    print(f"[DEBUG] QImage created - format: {qimg.format()}, depth: {qimg.depth()}, bytes per line: {qimg.bytesPerLine()}")

    # Force premultiplied + opaque background if needed
    qimg_premul = QImage(qimg.size(), QImage.Format_ARGB32_Premultiplied)
    qimg_premul.fill(QColor(30, 30, 30, 255))  # solid dark bg

    painter = QPainter(qimg_premul)
    painter.drawImage(0, 0, qimg)
    painter.end()

    pix = QPixmap.fromImage(qimg_premul)

    if pix.isNull():
        print("[ERROR] Final pixmap is null")
    else:
        print(f"[DEBUG] Pixmap OK - size: {pix.size()}, depth: {pix.depth()}")

    # Safety: if still invisible, return test green
    if pix.width() == 0 or pix.height() == 0:
        print("[DEBUG] Pixmap empty - returning green test")
        green = QPixmap(640, 480)
        green.fill(QColor(0, 255, 0))
        return green

    return pix