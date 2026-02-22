# widgets/pixmap_convert.py
"""Gentle helpers for turning text into beautiful preview pixmaps."""

import pygame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from utils.helpers import render_wrapped_text, pygame_surf_to_pixmap


def render_frame(
    wrapped_text: str,
    color: tuple[int, int, int],
    alpha: int = 255,
    width: int = 1920,
    height: int = 1080,
    font_size: int = 80,
) -> QPixmap:
    """Create one single beautiful frame — clean, reusable, and full of cozy magic."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    font = pygame.font.SysFont(None, font_size)

    # Render with the exact cozy margins we already love
    render_wrapped_text(surf, wrapped_text, font, 60, 80, (*color, alpha))

    pix = pygame_surf_to_pixmap(surf)
    return pix.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)