# utils/helpers.py
"""Helper functions for text wrapping and rendering."""

import pygame
import textwrap

from PySide6.QtGui import QImage, QPixmap  # ← added here

def wrap_text(text, width):
    """Soft-wrap text at word boundaries, preserve explicit newlines."""
    lines = text.splitlines(keepends=True)
    wrapped_lines = []
    for line in lines:
        if line == '\n':
            wrapped_lines.append('')
            continue
        wrapped = textwrap.wrap(line.rstrip('\n'), width=width, break_long_words=False)
        wrapped_lines.extend(wrapped)
    return '\n'.join(wrapped_lines)

def render_wrapped_text(surf, wrapped_text, font, x, y_start, color):
    """Render multi-line wrapped text onto a Pygame surface."""
    lines = wrapped_text.split('\n')
    y = y_start
    line_height = font.get_linesize()
    for line in lines:
        if not line:
            y += line_height
            continue
        line_surf = font.render(line, True, color)
        surf.blit(line_surf, (x, y))
        y += line_height

def pygame_surf_to_pixmap(surf):
    """Convert Pygame surface to QPixmap."""
    img_str = pygame.image.tostring(surf, 'RGBA')
    qimg = QImage(img_str, surf.get_width(), surf.get_height(), QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)