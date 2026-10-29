"""
menu_screen.py
--------------
Ecran d'accueil permettant de choisir la taille de la grille,
de lancer une nouvelle generation ou de reprendre un puzzle de l'historique.
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from storage.puzzle_store import PuzzleStore
from utils.config import (
    COLOR_BG,
    COLOR_ACCENT,
    COLOR_TEXT_DARK,
    GRID_SIZES,
    DEFAULT_GRID_SIZE,
    FONT_TITLE,
    FONT_BUTTON,
)


class MenuScreen(tk.Frame):
    """
    Ecran principal d'accueil et de gestion de l'historique des puzzles.
    """

    def __init__(
        self,
        parent: tk.Widget,
        puzzle_store: PuzzleStore,
        on_start_new_game: Callable[[str], None],
        on_resume_game: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self.puzzle_store = puzzle_store
        self.on_start_new_game = on_start_new_game
        self.on_resume_game = on_resume_game

        self.selected_size_var = tk.StringVar(value=DEFAULT_GRID_SIZE)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construit l'interface du menu d'accueil."""
        # En-tete
        header_frame = tk.Frame(self, bg=COLOR_BG, pady=15)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title = tk.Label(
            header_frame,
            text="Les Mots Codes",
            font=FONT_TITLE,
            bg=COLOR_BG,
            fg=COLOR_ACCENT,
        )
        title.pack()

        subtitle = tk.Label(
            header_frame,
            text="Jeu de mots croises chiffres d'apres Jean Paul Cordier",
            font=("Helvetica", 11, "italic"),
            bg=COLOR_BG,
            fg="#666666",
        )
        subtitle.pack(pady=4)

        # Section Nouvelle Partie
        new_game_box = tk.LabelFrame(
            self,
            text=" Nouvelle Partie ",
            font=("Helvetica", 12, "bold"),
            bg=COLOR_BG,
            fg=COLOR_TEXT_DARK,
            padx=15,
            pady=15,
        )
        new_game_box.pack(side=tk.TOP, fill=tk.X, padx=25, pady=10)

        size_label = tk.Label(
            new_game_box,
            text="Choisissez la taille de la grille :",
            font=("Helvetica", 11),
            bg=COLOR_BG,
            fg=COLOR_TEXT_DARK,
        )
        size_label.pack(anchor="w", pady=(0, 5))

        radio_frame = tk.Frame(new_game_box, bg=COLOR_BG)
        radio_frame.pack(fill=tk.X, pady=5)

        for name, (w, h) in GRID_SIZES.items():
            rb = tk.Radiobutton(
                radio_frame,
                text=f"{name} ({w}x{h})",
                variable=self.selected_size_var,
                value=name,
                font=("Helvetica", 11),
                bg=COLOR_BG,
                activebackground=COLOR_BG,
                cursor="hand2",
            )
            rb.pack(side=tk.LEFT, padx=15)

        btn_start = tk.Button(
            new_game_box,
            text="Generer et Jouer",
            font=("Helvetica", 12, "bold"),
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._handle_start_click,
        )
        btn_start.pack(pady=(12, 0))

        # Section Historique des parties
        history_box = tk.LabelFrame(
            self,
            text=" Historique des Parties ",
            font=("Helvetica", 12, "bold"),
            bg=COLOR_BG,
            fg=COLOR_TEXT_DARK,
            padx=15,
            pady=10,
        )
        history_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=25, pady=(5, 15))

        # Tableau Treeview pour l'historique
        columns = ("date", "size", "time", "status")
        self.tree = ttk.Treeview(
            history_box,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=6,
        )
        self.tree.heading("date", text="Date de creation")
        self.tree.heading("size", text="Taille")
        self.tree.heading("time", text="Temps")
        self.tree.heading("status", text="Statut")

        self.tree.column("date", width=180, anchor="center")
        self.tree.column("size", width=100, anchor="center")
        self.tree.column("time", width=100, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(history_box, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda _: self._handle_resume_click())

        # Boutons d'action sur l'historique
        btn_hist_frame = tk.Frame(self, bg=COLOR_BG)
        btn_hist_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=(0, 15))

        btn_resume = tk.Button(
            btn_hist_frame,
            text="Reprendre la partie selectionnee",
            font=FONT_BUTTON,
            bg="#2E7D32",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._handle_resume_click,
        )
        btn_resume.pack(side=tk.LEFT, padx=5)

        btn_delete = tk.Button(
            btn_hist_frame,
            text="Supprimer",
            font=FONT_BUTTON,
            bg="#C62828",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._handle_delete_click,
        )
        btn_delete.pack(side=tk.LEFT, padx=5)

        btn_refresh = tk.Button(
            btn_hist_frame,
            text="Actualiser",
            font=FONT_BUTTON,
            bg="#666666",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.refresh_history,
        )
        btn_refresh.pack(side=tk.RIGHT, padx=5)

        self.refresh_history()

    def refresh_history(self) -> None:
        """Recharge la liste des parties sauvegardees."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        puzzles = self.puzzle_store.list_puzzles()
        for p in puzzles:
            created_str = p.get("created_at", "")
            try:
                dt = datetime.fromisoformat(created_str)
                display_date = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                display_date = created_str[:16]

            size_str = f"{p.get('width', 0)}x{p.get('height', 0)}"

            sec = p.get("elapsed_seconds", 0)
            time_str = f"{sec // 60:02d}:{sec % 60:02d}"

            status_str = "Termine" if p.get("is_completed") else "En cours"

            self.tree.insert(
                "",
                tk.END,
                iid=p["puzzle_id"],
                values=(display_date, size_str, time_str, status_str),
            )

    def _handle_start_click(self) -> None:
        """Declenche la generation d'une nouvelle grille avec la taille choisie."""
        size_label = self.selected_size_var.get()
        self.on_start_new_game(size_label)

    def _handle_resume_click(self) -> None:
        """Reprend la partie selectionnee dans l'historique."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection", "Veuillez selectionner une partie dans la liste.")
            return

        puzzle_id = selected[0]
        self.on_resume_game(puzzle_id)

    def _handle_delete_click(self) -> None:
        """Supprime la partie selectionnee de l'historique."""
        selected = self.tree.selection()
        if not selected:
            return

        puzzle_id = selected[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous supprimer cette partie ?"):
            self.puzzle_store.delete_puzzle(puzzle_id)
            self.refresh_history()

