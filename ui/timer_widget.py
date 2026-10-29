"""
timer_widget.py
---------------
Widget Tkinter pour afficher le chronometre et controler la pause.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from utils.config import (
    COLOR_BG,
    COLOR_ACCENT,
    COLOR_TEXT_DARK,
    FONT_TIMER,
    FONT_BUTTON,
)


class TimerWidget(tk.Frame):
    """
    Composant d'affichage du chronometre avec bouton pause/reprise.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_pause_toggle: Optional[Callable[[bool], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self.on_pause_toggle = on_pause_toggle

        self._elapsed_seconds = 0
        self._is_paused = False
        self._is_running = False
        self._after_id: Optional[str] = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Cree les composants visuels du chronometre."""
        self.time_label = tk.Label(
            self,
            text="00:00",
            font=FONT_TIMER,
            bg=COLOR_BG,
            fg=COLOR_TEXT_DARK,
            padx=10,
        )
        self.time_label.pack(side=tk.LEFT)

        self.pause_button = tk.Button(
            self,
            text="Pause",
            font=FONT_BUTTON,
            command=self._handle_pause_click,
            relief=tk.FLAT,
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            padx=8,
            pady=2,
            cursor="hand2",
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

    def _handle_pause_click(self) -> None:
        """Gere le clic sur le bouton pause/reprise."""
        self._is_paused = not self._is_paused
        self._update_button_text()
        if self.on_pause_toggle:
            self.on_pause_toggle(self._is_paused)

    def _update_button_text(self) -> None:
        """Met a jour le texte du bouton selon l'etat."""
        if self._is_paused:
            self.pause_button.config(text="Reprendre", bg="#2E7D32")
        else:
            self.pause_button.config(text="Pause", bg=COLOR_ACCENT)

    def set_time(self, seconds: int) -> None:
        """Definit le temps actuel du chronometre."""
        self._elapsed_seconds = max(0, seconds)
        self._render_time()

    def set_paused(self, is_paused: bool) -> None:
        """Definit l'etat de pause sans declencher le callback."""
        self._is_paused = is_paused
        self._update_button_text()

    def start(self) -> None:
        """Demarre ou reprend le decompte du temps."""
        if self._is_running:
            return
        self._is_running = True
        self._tick()

    def stop(self) -> None:
        """Arrete le decompte du temps."""
        self._is_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _tick(self) -> None:
        """Boucle periodique executee chaque seconde."""
        if not self._is_running:
            return

        if not self._is_paused:
            self._elapsed_seconds += 1
            self._render_time()

        self._after_id = self.after(1000, self._tick)

    def _render_time(self) -> None:
        """Met a jour l'affichage MM:SS ou HH:MM:SS."""
        total = self._elapsed_seconds
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60

        if hours > 0:
            formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            formatted = f"{minutes:02d}:{seconds:02d}"

        self.time_label.config(text=formatted)

    def get_elapsed_seconds(self) -> int:
        """Retourne le nombre total de secondes ecoulees."""
        return self._elapsed_seconds

