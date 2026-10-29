"""
app.py
------
Fenetre principale de l'application Les Mots Codes.
Gere la navigation entre l'ecran de menu et l'ecran de jeu,
la synchronisation entre la grille et le panneau de saisie,
l'auto-sauvegarde et la detection de victoire.
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
    COLOR_BG,
    COLOR_ACCENT,
    COLOR_TEXT_LIGHT,
    FONT_BUTTON,
    GRID_SIZES,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)


class MotsCodesApp(tk.Tk):
    """
    Application principale Tkinter.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(bg=COLOR_BG)

        # Initialisation des gestionnaires de donnees
        self.store = PuzzleStore()
        self.generator = GridGenerator()
        self.current_game: Optional[GameModel] = None

        # Conteneur principal
        self.container = tk.Frame(self, bg=COLOR_BG)
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
        )

        # 2. Ecran de jeu
        self.game_frame = tk.Frame(self.container, bg=COLOR_BG)

        # Barre superieure de jeu
        self.header_frame = tk.Frame(self.game_frame, bg=COLOR_BG, pady=8, padx=15)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_back = tk.Button(
            self.header_frame,
            text="< Retour au Menu",
            font=FONT_BUTTON,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT_LIGHT,
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.show_menu,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.info_label = tk.Label(
            self.header_frame,
            text="",
            font=("Helvetica", 11, "bold"),
            bg=COLOR_BG,
            fg="#555555",
            padx=20,
        )
        self.info_label.pack(side=tk.LEFT)

        self.timer_widget = TimerWidget(
            self.header_frame,
            on_pause_toggle=self._on_pause_toggle,
        )
        self.timer_widget.pack(side=tk.RIGHT)

        # Zone centrale de jeu (grille au centre, panneau de code a droite)
        self.play_area = tk.Frame(self.game_frame, bg=COLOR_BG)
        self.play_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.code_panel = CodePanel(
            self.play_area,
            on_code_changed=self._on_code_changed,
            width=240,
        )
        self.code_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.grid_view = GridView(
            self.play_area,
            on_cell_clicked=self._on_cell_clicked,
        )
        self.grid_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Gestion des touches clavier directes sur la grille
        self.bind("<Key>", self._on_global_key)

    def show_menu(self) -> None:
        """Affiche l'ecran de menu et sauvegarde l'eventuelle partie en cours."""
        if self.current_game:
            self._save_current_state()
            self.timer_widget.stop()

        self.game_frame.pack_forget()
        self.menu_screen.refresh_history()
        self.menu_screen.pack(fill=tk.BOTH, expand=True)

    def show_game(self) -> None:
        """Bascule l'affichage sur l'ecran de jeu."""
        self.menu_screen.pack_forget()
        self.game_frame.pack(fill=tk.BOTH, expand=True)

    def start_new_game(self, size_label: str) -> None:
        """Genere une nouvelle grille et lance la partie."""
        width, height = GRID_SIZES.get(size_label, (13, 13))

        generated_grid = self.generator.generate(width, height)
        if not generated_grid:
            messagebox.showerror("Erreur", "Impossible de generer une grille avec cette taille.")
            return

        puzzle = PuzzleEncoder.encode(generated_grid)
        game = GameModel.new_game(puzzle)

        self._load_game_into_ui(game)

    def resume_game(self, puzzle_id: str) -> None:
        """Reprend une partie existante depuis son identifiant."""
        game = self.store.load_puzzle(puzzle_id)
        if not game:
            messagebox.showerror("Erreur", "Impossible de charger la partie demandee.")
            return

        self._load_game_into_ui(game)

    def _load_game_into_ui(self, game: GameModel) -> None:
        """Charge un GameModel dans l'interface et demarre."""
        self.current_game = game

        self.info_label.config(
            text=f"Grille {game.width}x{game.height} — {len(game.initial_hints)} indices"
        )

        self.grid_view.set_game(game)
        self.code_panel.load_state(game.initial_hints, game.player_mapping)

        self.timer_widget.set_time(game.elapsed_seconds)
        self.timer_widget.set_paused(game.is_paused)

        self.show_game()

        if not game.is_completed:
            self.timer_widget.start()
        else:
            self.timer_widget.stop()

    def _on_code_changed(self, code: int, letter: Optional[str]) -> None:
        """Declenche lors de la saisie d'une lettre dans le panneau lateral."""
        if not self.current_game:
            return

        is_completed = self.current_game.set_letter_for_code(code, letter)
        self.grid_view.redraw()
        self._save_current_state()

        if is_completed:
            self._handle_victory()

    def _on_cell_clicked(self, row: int, col: int, code: int) -> None:
        """Met en evidence le champ du panneau lateral lorsqu'une case est cliquee."""
        if code in self.code_panel._entries:
            self.code_panel._entries[code].focus_set()

    def _on_global_key(self, event: tk.Event) -> None:
        """Permet de taper directement sur le clavier pour la case selectionnee."""
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
        """Gere la mise en pause depuis le widget chronometre."""
        if self.current_game:
            self.current_game.is_paused = is_paused
            self._save_current_state()

    def _save_current_state(self) -> None:
        """Persiste l'etat actuel du puzzle."""
        if self.current_game:
            self.current_game.elapsed_seconds = self.timer_widget.get_elapsed_seconds()
            self.store.save_puzzle(self.current_game)

    def _handle_victory(self) -> None:
        """Affiche la fenetre de victoire."""
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
        """Sauvegarde avant de quitter l'application."""
        if self.current_game:
            self._save_current_state()
        self.destroy()

