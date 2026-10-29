"""
code_panel.py
-------------
Panneau lateral affichant les 26 codes (1 a 26) et permettant au joueur
de saisir la lettre associee a chaque code.
"""

import tkinter as tk
from typing import Callable, Optional

from utils.config import (
    COLOR_BG,
    COLOR_ACCENT,
    COLOR_CELL_HINT,
    COLOR_TEXT_DARK,
    FONT_CODE,
    FONT_BUTTON,
    NUM_CODES,
)


class CodePanel(tk.Frame):
    """
    Panneau interactif de saisie des 26 correspondances chiffre -> lettre.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_code_changed: Optional[Callable[[int, Optional[str]], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self.on_code_changed = on_code_changed

        self._entries: dict[int, tk.Entry] = {}
        self._vars: dict[int, tk.StringVar] = {}
        self._hint_codes: set[int] = set()

        self._build_ui()

    def _build_ui(self) -> None:
        """Construit la grille de saisie des 26 codes sur 2 colonnes de 13."""
        title_label = tk.Label(
            self,
            text="Correspondances (1-26)",
            font=("Helvetica", 12, "bold"),
            bg=COLOR_BG,
            fg=COLOR_TEXT_DARK,
            pady=8,
        )
        title_label.pack(side=tk.TOP, fill=tk.X)

        container = tk.Frame(self, bg=COLOR_BG)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Disposition en 2 colonnes de 13 lignes
        for idx in range(1, NUM_CODES + 1):
            col_idx = 0 if idx <= 13 else 1
            row_idx = (idx - 1) if idx <= 13 else (idx - 14)

            cell_frame = tk.Frame(
                container,
                bg="#FFFFFF",
                bd=1,
                relief=tk.SOLID,
                padx=2,
                pady=2,
            )
            cell_frame.grid(row=row_idx, column=col_idx, padx=4, pady=2, sticky="ew")

            num_label = tk.Label(
                cell_frame,
                text=f"{idx:2d}",
                font=("Courier", 10, "bold"),
                width=3,
                bg="#E0E0E0",
                fg=COLOR_TEXT_DARK,
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
            )
            entry.pack(side=tk.LEFT)

            # Liaison des evenements clavier
            entry.bind("<KeyRelease>", lambda event, c=idx: self._on_key(c, event))

            self._vars[idx] = var
            self._entries[idx] = entry

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

    def load_state(
        self,
        hints: dict[int, str],
        player_mapping: dict[int, str],
    ) -> None:
        """
        Charge les indices et les saisies existantes du joueur.
        """
        self._hint_codes = set(hints.keys())

        for code in range(1, NUM_CODES + 1):
            entry = self._entries[code]
            var = self._vars[code]

            if code in self._hint_codes:
                letter = hints[code]
                var.set(letter)
                entry.config(state="readonly", readonlybackground=COLOR_CELL_HINT)
            else:
                letter = player_mapping.get(code, "")
                var.set(letter)
                entry.config(state="normal", bg="#FFFFFF")

    def _on_key(self, code: int, event: tk.Event) -> None:
        """Traite la saisie dans un champ de code."""
        if code in self._hint_codes:
            return

        var = self._vars[code]
        raw_text = var.get()

        # Ne garder que la derniere lettre alphabetique tapee
        clean_text = "".join(ch for ch in raw_text if ch.isalpha()).upper()

        if len(clean_text) > 1:
            clean_text = clean_text[-1]

        var.set(clean_text)

        # Notification du changement
        if self.on_code_changed:
            self.on_code_changed(code, clean_text if clean_text else None)

        # Passer automatiquement au champ vide suivant si une lettre est entree
        if clean_text:
            next_code = self._find_next_unfilled_code(code)
            if next_code:
                self._entries[next_code].focus_set()

    def _find_next_unfilled_code(self, current_code: int) -> Optional[int]:
        """Cherche le prochain code non rempli pour faciliter la frappe."""
        for c in range(current_code + 1, NUM_CODES + 1):
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

