"""
menu_screen.py
--------------
Ecran d'accueil permettant de choisir la taille de la grille (dont 9x17),
de lancer une generation, de reprendre un puzzle de l'historique
et de basculer entre le Mode Clair et le Mode Sombre.
Boutons a tres fort contraste et ergonomie soignee.
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from storage.puzzle_store import PuzzleStore
from utils.config import (
    THEME_LIGHT,
    THEME_DARK,
    GRID_SIZES,
    DEFAULT_GRID_SIZE,
    FONT_TITLE,
    FONT_BUTTON,
)


class MenuScreen(tk.Frame):
    """
    Ecran principal d'accueil, historique des puzzles et selecteur de theme.
    """

    def __init__(
        self,
        parent: tk.Widget,
        puzzle_store: PuzzleStore,
        on_start_new_game: Callable[[str], None],
        on_resume_game: Callable[[str], None],
        on_toggle_theme: Callable[[], None],
        theme: dict = THEME_LIGHT,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=theme["bg"], **kwargs)
        self.puzzle_store = puzzle_store
        self.on_start_new_game = on_start_new_game
        self.on_resume_game = on_resume_game
        self.on_toggle_theme = on_toggle_theme
        self.theme = theme

        self.selected_size_var = tk.StringVar(value=DEFAULT_GRID_SIZE)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construit l'interface du menu d'accueil avec un design soigne."""
        # Barre superieure avec Titre et Bouton Theme
        self.top_bar = tk.Frame(self, bg=self.theme["bg"], pady=14, padx=25)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        header_center = tk.Frame(self.top_bar, bg=self.theme["bg"])
        header_center.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.title_label = tk.Label(
            header_center,
            text="Les Mots Codes",
            font=FONT_TITLE,
            bg=self.theme["bg"],
            fg=self.theme["accent"],
            anchor="w",
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            header_center,
            text="Jeu de mots croises chiffres d'apres Jean Paul Cordier",
            font=("Helvetica", 11, "italic"),
            bg=self.theme["bg"],
            fg=self.theme["text_muted"],
            anchor="w",
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Bouton bascule de theme
        theme_btn_text = "Mode Sombre" if self.theme["name"] == "light" else "Mode Clair"
        self.btn_theme = tk.Button(
            self.top_bar,
            text=theme_btn_text,
            font=FONT_BUTTON,
            bg=self.theme["btn_theme_bg"],
            fg=self.theme["btn_theme_fg"],
            activebackground=self.theme["card_bg"],
            activeforeground=self.theme["text_dark"],
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.on_toggle_theme,
        )
        self.btn_theme.pack(side=tk.RIGHT, padx=5)

        # Section Nouvelle Partie
        self.new_game_box = tk.LabelFrame(
            self,
            text=" Nouvelle Partie ",
            font=("Helvetica", 12, "bold"),
            bg=self.theme["card_bg"],
            fg=self.theme["text_dark"],
            bd=1,
            relief=tk.SOLID,
            padx=20,
            pady=16,
        )
        self.new_game_box.pack(side=tk.TOP, fill=tk.X, padx=25, pady=10)

        self.size_label = tk.Label(
            self.new_game_box,
            text="Choisissez la taille de la grille (grille dense, <= 10% cases noires) :",
            font=("Helvetica", 11),
            bg=self.theme["card_bg"],
            fg=self.theme["text_dark"],
        )
        self.size_label.pack(anchor="w", pady=(0, 10))

        self.radio_frame = tk.Frame(self.new_game_box, bg=self.theme["card_bg"])
        self.radio_frame.pack(fill=tk.X, pady=5)

        self.radio_buttons = []
        for name, (w, h) in GRID_SIZES.items():
            extra_info = " (recommandee)" if name == "Moyenne" else ""
            rb = tk.Radiobutton(
                self.radio_frame,
                text=f"{name} : {h} lignes x {w} colonnes{extra_info}",
                variable=self.selected_size_var,
                value=name,
                font=("Helvetica", 11, "bold" if name == "Moyenne" else "normal"),
                bg=self.theme["card_bg"],
                fg=self.theme["text_dark"],
                activebackground=self.theme["card_bg"],
                activeforeground=self.theme["text_dark"],
                selectcolor=self.theme["card_bg"],
                cursor="hand2",
            )
            rb.pack(side=tk.LEFT, padx=15)
            self.radio_buttons.append(rb)

        self.btn_start = tk.Button(
            self.new_game_box,
            text="Generer et Jouer",
            font=("Helvetica", 12, "bold"),
            bg=self.theme["btn_primary_bg"],
            fg=self.theme["btn_primary_fg"],
            activebackground=self.theme["accent_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self._handle_start_click,
        )
        self.btn_start.pack(pady=(16, 2))

        # Section Historique des parties
        self.history_box = tk.LabelFrame(
            self,
            text=" Historique des Parties ",
            font=("Helvetica", 12, "bold"),
            bg=self.theme["card_bg"],
            fg=self.theme["text_dark"],
            bd=1,
            relief=tk.SOLID,
            padx=15,
            pady=12,
        )
        self.history_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=25, pady=(5, 12))

        columns = ("date", "size", "time", "status")
        self.tree = ttk.Treeview(
            self.history_box,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=6,
        )
        self.tree.heading("date", text="Date de creation")
        self.tree.heading("size", text="Taille (lignes x colonnes)")
        self.tree.heading("time", text="Temps")
        self.tree.heading("status", text="Statut")

        self.tree.column("date", width=180, anchor="center")
        self.tree.column("size", width=170, anchor="center")
        self.tree.column("time", width=110, anchor="center")
        self.tree.column("status", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(self.history_box, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda _: self._handle_resume_click())

        # Boutons d'action sur l'historique
        self.btn_hist_frame = tk.Frame(self, bg=self.theme["bg"])
        self.btn_hist_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=(0, 16))

        self.btn_resume = tk.Button(
            self.btn_hist_frame,
            text="Reprendre la partie selectionnee",
            font=FONT_BUTTON,
            bg=self.theme["btn_success_bg"],
            fg=self.theme["btn_success_fg"],
            activebackground="#14532D",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._handle_resume_click,
        )
        self.btn_resume.pack(side=tk.LEFT, padx=5)

        self.btn_delete = tk.Button(
            self.btn_hist_frame,
            text="Supprimer",
            font=FONT_BUTTON,
            bg=self.theme["btn_danger_bg"],
            fg=self.theme["btn_danger_fg"],
            activebackground="#7F1D1D",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._handle_delete_click,
        )
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = tk.Button(
            self.btn_hist_frame,
            text="Actualiser",
            font=FONT_BUTTON,
            bg=self.theme["btn_secondary_bg"],
            fg=self.theme["btn_secondary_fg"],
            activebackground="#1E293B",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.refresh_history,
        )
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)

        self._configure_tree_style()
        self.refresh_history()

    def _configure_tree_style(self) -> None:
        """Adapte le style du Treeview selon le theme."""
        style = ttk.Style()
        style.theme_use("default")

        bg = self.theme["card_bg"]
        fg = self.theme["text_dark"]
        selected_bg = self.theme["accent"]

        style.configure(
            "Treeview",
            background=bg,
            foreground=fg,
            fieldbackground=bg,
            rowheight=28,
            font=("Helvetica", 10),
        )
        style.map(
            "Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", "#FFFFFF")],
        )
        style.configure(
            "Treeview.Heading",
            background=self.theme["bg"],
            foreground=fg,
            font=("Helvetica", 10, "bold"),
            relief="flat",
        )

    def apply_theme(self, theme: dict) -> None:
        """Applique les couleurs du theme a l'ensemble des composants du menu."""
        self.theme = theme
        self.config(bg=theme["bg"])
        self.top_bar.config(bg=theme["bg"])

        self.title_label.config(bg=theme["bg"], fg=theme["accent"])
        self.subtitle_label.config(bg=theme["bg"], fg=theme["text_muted"])
        self.btn_hist_frame.config(bg=theme["bg"])

        theme_btn_text = "Mode Sombre" if theme["name"] == "light" else "Mode Clair"
        self.btn_theme.config(
            text=theme_btn_text,
            bg=theme["btn_theme_bg"],
            fg=theme["btn_theme_fg"],
        )

        self.new_game_box.config(
            bg=theme["card_bg"],
            fg=theme["text_dark"],
        )
        self.size_label.config(bg=theme["card_bg"], fg=theme["text_dark"])
        self.radio_frame.config(bg=theme["card_bg"])

        for rb in self.radio_buttons:
            rb.config(
                bg=theme["card_bg"],
                fg=theme["text_dark"],
                activebackground=theme["card_bg"],
                activeforeground=theme["text_dark"],
                selectcolor=theme["card_bg"],
            )

        self.btn_start.config(
            bg=theme["btn_primary_bg"],
            fg=theme["btn_primary_fg"],
            activebackground=theme["accent_hover"],
        )

        self.history_box.config(
            bg=theme["card_bg"],
            fg=theme["text_dark"],
        )

        self.btn_resume.config(
            bg=theme["btn_success_bg"],
            fg=theme["btn_success_fg"],
        )
        self.btn_delete.config(
            bg=theme["btn_danger_bg"],
            fg=theme["btn_danger_fg"],
        )
        self.btn_refresh.config(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
        )

        self._configure_tree_style()

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

            size_str = f"{p.get('height', 0)} l. x {p.get('width', 0)} col."

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
