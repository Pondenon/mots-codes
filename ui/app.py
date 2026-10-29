"""
app.py
------
Fenetre principale de l'application Les Mots Codes.
Gere :
- La navigation entre le menu et l'ecran de jeu.
- Le Mode Clair et le Mode Sombre basculables sur chaque page.
- Des boutons a fort contraste et tres lisibles.
- L'adaptation dynamique aux tailles (dont Moyenne = 9 lignes x 17 colonnes).
- La selection intelligente des indices (consonnes, 18-22% de couverture).
- L'auto-sauvegarde et la detection de victoire.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from core.encoder import PuzzleEncoder
from core.game_model import GameModel
from core.grid_generator import GridGenerator
from storage.puzzle_store import PuzzleStore
from ui.code_panel import CodePanel
from ui.grid_view import GridView
from ui.menu_screen import MenuScreen
from ui.timer_widget import TimerWidget
from utils.config import (
    APP_TITLE,
    THEME_LIGHT,
    THEME_DARK,
    GRID_SIZES,
    DEFAULT_GRID_SIZE,
    FONT_BUTTON,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)


class MotsCodesApp(tk.Tk):
    """
    Application principale Tkinter avec support dynamique du theme clair/sombre.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Theme actif par defaut : Mode Clair moderne
        self.theme = THEME_LIGHT
        self.configure(bg=self.theme["bg"])

        self.store = PuzzleStore()
        self.generator = GridGenerator()
        self.current_game: Optional[GameModel] = None

        self.container = tk.Frame(self, bg=self.theme["bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        self._build_screens()
        self.show_menu()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_screens(self) -> None:
        """Construit l'ecran de menu et l'ecran de jeu."""
        # 1. Ecran de menu
        self.menu_screen = MenuScreen(
            parent=self.container,
            puzzle_store=self.store,
            on_start_new_game=self.start_new_game,
            on_resume_game=self.resume_game,
            on_toggle_theme=self.toggle_theme,
            theme=self.theme,
        )

        # 2. Ecran de jeu
        self.game_frame = tk.Frame(self.container, bg=self.theme["bg"])

        # Barre superieure de jeu
        self.header_frame = tk.Frame(self.game_frame, bg=self.theme["bg"], pady=12, padx=20)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_back = tk.Button(
            self.header_frame,
            text="< Retour au Menu",
            font=FONT_BUTTON,
            bg=self.theme["btn_primary_bg"],
            fg=self.theme["btn_primary_fg"],
            activebackground=self.theme["accent_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.show_menu,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.info_label = tk.Label(
            self.header_frame,
            text="",
            font=("Helvetica", 11, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["text_muted"],
            padx=20,
        )
        self.info_label.pack(side=tk.LEFT)

        # Bouton theme sur la page de jeu
        theme_btn_text = "Mode Sombre" if self.theme["name"] == "light" else "Mode Clair"
        self.btn_theme_game = tk.Button(
            self.header_frame,
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
            command=self.toggle_theme,
        )
        self.btn_theme_game.pack(side=tk.RIGHT, padx=(10, 0))

        self.timer_widget = TimerWidget(
            self.header_frame,
            on_pause_toggle=self._on_pause_toggle,
            theme=self.theme,
        )
        self.timer_widget.pack(side=tk.RIGHT)

        # Zone centrale de jeu
        self.play_area = tk.Frame(self.game_frame, bg=self.theme["bg"])
        self.play_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        self.code_panel = CodePanel(
            self.play_area,
            on_code_changed=self._on_code_changed,
            theme=self.theme,
            width=260,
        )
        self.code_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        self.grid_view = GridView(
            self.play_area,
            on_cell_clicked=self._on_cell_clicked,
            theme=self.theme,
        )
        self.grid_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.bind("<Key>", self._on_global_key)

    def toggle_theme(self) -> None:
        """Bascule entre le mode clair et le mode sombre."""
        self.theme = THEME_DARK if self.theme["name"] == "light" else THEME_LIGHT
        self._apply_current_theme()

    def _apply_current_theme(self) -> None:
        """Met a jour l'apparence de tous les composants selon le theme actif."""
        self.configure(bg=self.theme["bg"])
        self.container.config(bg=self.theme["bg"])
        self.game_frame.config(bg=self.theme["bg"])
        self.header_frame.config(bg=self.theme["bg"])
        self.play_area.config(bg=self.theme["bg"])

        self.info_label.config(bg=self.theme["bg"], fg=self.theme["text_muted"])

        theme_btn_text = "Mode Sombre" if self.theme["name"] == "light" else "Mode Clair"
        self.btn_theme_game.config(
            text=theme_btn_text,
            bg=self.theme["btn_theme_bg"],
            fg=self.theme["btn_theme_fg"],
        )

        self.btn_back.config(
            bg=self.theme["btn_primary_bg"],
            fg=self.theme["btn_primary_fg"],
            activebackground=self.theme["accent_hover"],
        )

        self.menu_screen.apply_theme(self.theme)
        self.timer_widget.apply_theme(self.theme)
        self.grid_view.apply_theme(self.theme)
        self.code_panel.apply_theme(self.theme)

    def show_menu(self) -> None:
        """Affiche l'ecran d'accueil."""
        if self.current_game:
            self._save_current_state()
            self.timer_widget.stop()

        self.game_frame.pack_forget()
        self.menu_screen.refresh_history()
        self.menu_screen.pack(fill=tk.BOTH, expand=True)

    def show_game(self) -> None:
        """Bascule l'affichage sur la grille de jeu."""
        self.menu_screen.pack_forget()
        self.game_frame.pack(fill=tk.BOTH, expand=True)

    def start_new_game(self, size_label: str) -> None:
        """Genere une nouvelle grille dense avec la taille choisie."""
        width, height = GRID_SIZES.get(size_label, (17, 9))

        generated_grid = self.generator.generate(width, height)
        if not generated_grid:
            messagebox.showerror("Erreur", "Impossible de generer une grille pour cette taille.")
            return

        puzzle = PuzzleEncoder.encode(generated_grid)
        game = GameModel.new_game(puzzle)

        self._load_game_into_ui(game)

    def resume_game(self, puzzle_id: str) -> None:
        """Reprend une partie existante."""
        game = self.store.load_puzzle(puzzle_id)
        if not game:
            messagebox.showerror("Erreur", "Impossible de charger la partie demandee.")
            return

        self._load_game_into_ui(game)

    def _load_game_into_ui(self, game: GameModel) -> None:
        """Injecte l'etat de partie dans les composants visuels."""
        self.current_game = game

        # Calcul de la couverture des indices
        total_white = sum(
            1 for r in range(game.height) for c in range(game.width)
            if game.is_white(r, c)
        )
        hint_cells = sum(
            1 for r in range(game.height) for c in range(game.width)
            if game.is_white(r, c) and game.is_hint(game.encoded_grid[r][c])
        )
        coverage_pct = (hint_cells / total_white * 100) if total_white else 0

        self.info_label.config(
            text=f"Grille {game.height} l. x {game.width} col. — {game.num_codes} codes (1-{game.num_codes}) — Indices : {len(game.initial_hints)} consonnes ({coverage_pct:.0f}% des cases)"
        )

        self.grid_view.set_game(game)
        self.code_panel.load_state(
            hints=game.initial_hints,
            player_mapping=game.player_mapping,
            num_codes=game.num_codes,
            theme=self.theme,
        )

        self.timer_widget.set_time(game.elapsed_seconds)
        self.timer_widget.set_paused(game.is_paused)

        self.show_game()

        if not game.is_completed:
            self.timer_widget.start()
        else:
            self.timer_widget.stop()

    def _on_code_changed(self, code: int, letter: Optional[str]) -> None:
        """Declenche quand le joueur modifie une association code -> lettre."""
        if not self.current_game:
            return

        is_completed = self.current_game.set_letter_for_code(code, letter)
        self.grid_view.redraw()
        self._save_current_state()

        if is_completed:
            self._handle_victory()

    def _on_cell_clicked(self, row: int, col: int, code: int) -> None:
        """Selectionne la case et donne le focus a son entree correspondante."""
        if code in self.code_panel._entries:
            self.code_panel._entries[code].focus_set()

    def _on_global_key(self, event: tk.Event) -> None:
        """Permet la saisie directe au clavier sur la case selectionnee de la grille."""
        if not self.current_game or self.current_game.is_completed:
            return

        selected = self.grid_view._selected_cell
        if not selected:
            return

        r, c = selected
        code = self.current_game.get_code(r, c)
        if code is None or self.current_game.is_hint(code):
            return

        if event.char and event.char.isalpha():
            letter = event.char.upper()
            self.code_panel.update_code_display(code, letter)
            self._on_code_changed(code, letter)
        elif event.keysym in ("BackSpace", "Delete"):
            self.code_panel.update_code_display(code, "")
            self._on_code_changed(code, None)

    def _on_pause_toggle(self, is_paused: bool) -> None:
        """Gere la mise en pause depuis le chronometre."""
        if self.current_game:
            self.current_game.is_paused = is_paused
            self._save_current_state()

    def _save_current_state(self) -> None:
        """Persiste l'etat actuel du puzzle."""
        if self.current_game:
            self.current_game.elapsed_seconds = self.timer_widget.get_elapsed_seconds()
            self.store.save_puzzle(self.current_game)

    def _handle_victory(self) -> None:
        """Affiche l'alerte de victoire."""
        self.timer_widget.stop()
        self._save_current_state()

        seconds = self.current_game.elapsed_seconds
        mins = seconds // 60
        secs = seconds % 60
        time_text = f"{mins} minute(s) et {secs} seconde(s)" if mins > 0 else f"{secs} secondes"

        messagebox.showinfo(
            "Felicitation !",
            f"Bravo ! Vous avez resolu l'integralite de la grille de mots codes !\n\nTemps realise : {time_text}",
        )

    def _on_close(self) -> None:
        """Sauvegarde avant fermeture de la fenetre."""
        if self.current_game:
            self._save_current_state()
        self.destroy()
