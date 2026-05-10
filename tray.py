"""Системный трей J.A.R.V.I.S. — иконка в панели задач Windows."""
import io
import tkinter as tk
from typing import Callable, Optional

import pystray
from PIL import Image, ImageDraw


class TrayIcon:
    """Иконка в системном трее с меню."""

    def __init__(
        self,
        on_show: Callable,
        on_exit: Callable,
        tooltip: str = "J.A.R.V.I.S",
    ):
        self.on_show = on_show
        self.on_exit = on_exit
        self.tooltip = tooltip
        self.icon: Optional[pystray.Icon] = None
        self._thread = None

    # ------------------------------------------------------------------
    # Управление
    # ------------------------------------------------------------------
    def start(self):
        """Запустить иконку в трее (в отдельном потоке)."""
        image = self._create_image()
        menu = pystray.Menu(
            pystray.MenuItem("Открыть", self._show_window),
            pystray.MenuItem("Выход", self._exit_app),
        )
        self.icon = pystray.Icon("jarvis", image, self.tooltip, menu)
        self.icon.run_detached()

    def stop(self):
        """Убрать иконку из трея."""
        if self.icon:
            self.icon.stop()
            self.icon = None

    def notify(self, title: str, message: str):
        """Показать всплывающее уведомление из трея."""
        if self.icon:
            self.icon.notify(message, title)

    # ------------------------------------------------------------------
    # Callback-и меню
    # ------------------------------------------------------------------
    def _show_window(self, icon, item):
        self.on_show()

    def _exit_app(self, icon, item):
        self.on_exit()

    # ------------------------------------------------------------------
    # Генерация иконки (синий круг с буквой J)
    # ------------------------------------------------------------------
    def _create_image(self) -> Image.Image:
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), (0, 0, 0))
        dc = ImageDraw.Draw(image)

        # Синий круг (Apple Blue)
        dc.ellipse((0, 0, width, height), fill=(0, 122, 255))

        # Белая буква J по центру
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("segoeui.ttf", 36)
        except Exception:
            font = ImageFont.load_default()

        bbox = dc.textbbox((0, 0), "J", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 2
        dc.text((x, y), "J", font=font, fill=(255, 255, 255))

        return image
