"""
code_panel.py
-------------
Panneau lateral affichant les codes (de 1 a N, ou N est le nombre
de lettres uniques utilisees) et permettant au joueur de saisir la lettre
associee a chaque code. Supporte le mode sombre et le mode clair.
"""

import tkinter as tk
from typing import Callable, Optional

from utils.config import THEME_LIGHT, FONT_BUTTON


class CodePanel(tk.Frame):
    """
    Panneau interactif de saisie des N correspondances chiffre -> lettre.
    S'adapte dynamiquement au nombre exact de codes utilises dans le puzzle.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_code_changed: Optional[Callable[[int, Optional[str]], None]] = None,
        theme: dict = THEME_LIGHT,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=theme["bg"], **kwargs)
        self.on_code_changed = on_code_changed
        self.theme = theme

        self._entries: dict[int, tk.Entry] = {}
        self._vars: dict[int, tk.StringVar] = {}
        self._cell_frames: dict[int, tk.Frame] = {}
        self._num_labels: dict[int, tk.Label] = {}
        self._hint_codes: set[int] = set()
        self._num_codes: int = 26

        self.title_label = tk.Label(
            self,
            text="Correspondances (1-N)",
            font=("Helvetica", 12, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["text_dark"],
            pady=8,
        )
        self.title_label.pack(side=tk.TOP, fill=tk.X)

        self.container = tk.Frame(self, bg=self.theme["bg"])
        self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=5)

    def load_state(
        self,
        hints: dict[int, str],
        player_mapping: dict[int, str],
        num_codes: int,
        theme: Optional[dict] = None,
    ) -> None:
        """
        Reconstruit les champs de saisie pour codes 1 a num_codes.
        """
        if theme:
            self.theme = theme

        self._hint_codes = set(hints.keys())
        self._num_codes = max(1, num_codes)

        self.title_label.config(
            text=f"Correspondances (1-{self._num_codes})",
            bg=self.theme["bg"],
            fg=self.theme["text_dark"],
        )
        self.container.config(bg=self.theme["bg"])
        self.config(bg=self.theme["bg"])

        # Nettoyage des anciens widgets
        for widget in self.container.winfo_children():
            widget.destroy()

        self._entries.clear()
        self._vars.clear()
        self._cell_frames.clear()
        self._num_labels.clear()

        # Calcul de la disposition en 2 colonnes
        rows_per_col = (self._num_codes + 1) // 2

        for idx in range(1, self._num_codes + 1):
            col_idx = 0 if idx <= rows_per_col else 1
            row_idx = (idx - 1) if idx <= rows_per_col else (idx - 1 - rows_per_col)

            cell_frame = tk.Frame(
                self.container,
                bg=self.theme["card_bg"],
                bd=1,
                relief=tk.SOLID,
                padx=2,
                pady=2,
            )
            cell_frame.grid(row=row_idx, column=col_idx, padx=3, pady=2, sticky="ew")

            num_label = tk.Label(
                cell_frame,
                text=f"{idx:2d}",
                font=("Courier", 10, "bold"),
                width=3,
                bg=self.theme["bg"],
                fg=self.theme["text_dark"],
            )
            num_label.pack(side=tk.LEFT, padx=(0, 2))

            var = tk.StringVar()
            entry = tk.Entry(
                cell_frame,
                textvariable=var,
                font=("Helvetica", 11, "bold"),
                width=3,
                justify="center",
                relief=tk.FLAT,
                bg=self.theme["card_bg"],
                fg=self.theme["text_dark"],
                insertbackground=self.theme["text_dark"],
            )
            entry.pack(side=tk.LEFT)

            entry.bind("<KeyRelease>", lambda event, c=idx: self._on_key(c, event))

            self._vars[idx] = var
            self._entries[idx] = entry
            self._cell_frames[idx] = cell_frame
            self._num_labels[idx] = num_label

            if idx in self._hint_codes:
                letter = hints[idx]
                var.set(letter)
                entry.config(state="readonly", readonlybackground=self.theme["cell_hint"])
            else:
                letter = player_mapping.get(idx, "")
                var.set(letter)
                entry.config(state="normal", bg=self.theme["card_bg"])

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)

    def apply_theme(self, theme: dict) -> None:
        """Applique un nouveau theme (clair ou sombre)."""
        self.theme = theme
        self.config(bg=theme["bg"])
        self.title_label.config(bg=theme["bg"], fg=theme["text_dark"])
        self.container.config(bg=theme["bg"])

        for code, entry in self._entries.items():
            frame = self._cell_frames.get(code)
            lbl = self._num_labels.get(code)

            if frame:
                frame.config(bg=theme["card_bg"])
            if lbl:
                lbl.config(bg=theme["bg"], fg=theme["text_dark"])

            if code in self._hint_codes:
                entry.config(
                    readonlybackground=theme["cell_hint"],
                    fg=theme["text_dark"],
                )
            else:
                entry.config(
                    bg=theme["card_bg"],
                    fg=theme["text_dark"],
                    insertbackground=theme["text_dark"],
                )

    def _on_key(self, code: int, event: tk.Event) -> None:
        """Traite la saisie dans un champ de code."""
        if code in self._hint_codes:
            return

        var = self._vars[code]
        raw_text = var.get()

        clean_text = "".join(ch for ch in raw_text if ch.isalpha()).upper()
        if len(clean_text) > 1:
            clean_text = clean_text[-1]

        var.set(clean_text)

        if self.on_code_changed:
            self.on_code_changed(code, clean_text if clean_text else None)

        if clean_text:
            next_code = self._find_next_unfilled_code(code)
            if next_code:
                self._entries[next_code].focus_set()

    def _find_next_unfilled_code(self, current_code: int) -> Optional[int]:
        """Cherche le prochain code non rempli."""
        for c in range(current_code + 1, self._num_codes + 1):
            if c not in self._hint_codes and not self._vars[c].get():
                return c
        for c in range(1, current_code):
            if c not in self._hint_codes and not self._vars[c].get():
                return c
        return None

    def update_code_display(self, code: int, letter: Optional[str]) -> None:
        """Met a jour la lettre affichee pour un code precis."""
        if code in self._vars and code not in self._hint_codes:
            self._vars[code].set(letter.upper() if letter else "")
