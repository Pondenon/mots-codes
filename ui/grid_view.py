"""
grid_view.py
------------
Widget Tkinter Canvas affichant la grille de mots croises :
- Cases noires (separateurs)
- Cases blanches avec code en haut a gauche et lettre au centre
- Bordures normales et bordures en pointilles pour mots composes
- Selection interactive au clic
"""

import tkinter as tk
from typing import Callable, Optional

from core.game_model import GameModel
from utils.config import (
    COLOR_BG,
    COLOR_CELL_BLACK,
    COLOR_CELL_WHITE,
    COLOR_CELL_HINT,
    COLOR_CELL_FILLED,
    COLOR_BORDER_SOLID,
    COLOR_BORDER_DOTTED,
    COLOR_ACCENT,
    COLOR_TEXT_DARK,
    BORDER_DOTTED,
)


class GridView(tk.Frame):
    """
    Affichage graphique haute fidelite de la grille de mots codes sur un Canvas.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_cell_clicked: Optional[Callable[[int, int, int], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self.on_cell_clicked = on_cell_clicked

        self._game: Optional[GameModel] = None
        self._selected_cell: Optional[tuple[int, int]] = None
        self._cell_size: int = 40

        self.canvas = tk.Canvas(
            self,
            bg=COLOR_BG,
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

    def set_game(self, game: GameModel) -> None:
        """Associe un GameModel a la vue et redessine la grille."""
        self._game = game
        self._selected_cell = None
        self.redraw()

    def select_cell(self, row: int, col: int) -> None:
        """Selectionne visuellement une cellule blanche."""
        if self._game and self._game.is_white(row, col):
            self._selected_cell = (row, col)
            self.redraw()

    def _on_resize(self, event: tk.Event) -> None:
        """Adapte la taille des cases lors du redimensionnement de la fenetre."""
        self.redraw()

    def _on_click(self, event: tk.Event) -> None:
        """Detecte le clic de la souris sur une case."""
        if not self._game:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        margin = 15
        grid_pixel_w = self._game.width * self._cell_size
        grid_pixel_h = self._game.height * self._cell_size

        offset_x = max(margin, (canvas_width - grid_pixel_w) // 2)
        offset_y = max(margin, (canvas_height - grid_pixel_h) // 2)

        c = (event.x - offset_x) // self._cell_size
        r = (event.y - offset_y) // self._cell_size

        if 0 <= r < self._game.height and 0 <= c < self._game.width:
            if self._game.is_white(r, c):
                self._selected_cell = (r, c)
                self.redraw()
                code = self._game.get_code(r, c)
                if code is not None and self.on_cell_clicked:
                    self.on_cell_clicked(r, c, code)

    def redraw(self) -> None:
        """Dessine l'integralite de la grille sur le canvas."""
        self.canvas.delete("all")
        if not self._game:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 50 or canvas_h < 50:
            return

        margin = 20
        available_w = max(100, canvas_w - 2 * margin)
        available_h = max(100, canvas_h - 2 * margin)

        cell_w = available_w // self._game.width
        cell_h = available_h // self._game.height
        self._cell_size = max(24, min(cell_w, cell_h, 54))

        grid_pixel_w = self._game.width * self._cell_size
        grid_pixel_h = self._game.height * self._cell_size

        offset_x = (canvas_w - grid_pixel_w) // 2
        offset_y = (canvas_h - grid_pixel_h) // 2

        # Polices proportionnelles a la taille des cellules
        font_code_size = max(7, int(self._cell_size * 0.22))
        font_letter_size = max(11, int(self._cell_size * 0.48))
        font_code = ("Courier", font_code_size, "bold")
        font_letter = ("Helvetica", font_letter_size, "bold")

        # 1. Remplissage des cases
        for r in range(self._game.height):
            for c in range(self._game.width):
                x1 = offset_x + c * self._cell_size
                y1 = offset_y + r * self._cell_size
                x2 = x1 + self._cell_size
                y2 = y1 + self._cell_size

                if not self._game.is_white(r, c):
                    # Case noire
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=COLOR_CELL_BLACK,
                        outline=COLOR_CELL_BLACK,
                    )
                else:
                    # Case blanche
                    code = self._game.get_code(r, c)
                    letter = self._game.get_player_letter(r, c)
                    is_hint = code is not None and self._game.is_hint(code)
                    is_selected = (self._selected_cell == (r, c))

                    if is_selected:
                        fill_color = "#FFF9C4"  # surbrillance jaune pale
                    elif is_hint:
                        fill_color = COLOR_CELL_HINT
                    elif self._game.is_completed:
                        fill_color = COLOR_CELL_FILLED
                    else:
                        fill_color = COLOR_CELL_WHITE

                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=fill_color,
                        outline="",
                    )

                    # Numero de code en haut a gauche
                    if code is not None:
                        self.canvas.create_text(
                            x1 + 3,
                            y1 + 2,
                            text=str(code),
                            font=font_code,
                            anchor="nw",
                            fill="#666666" if not is_hint else COLOR_ACCENT,
                        )

                    # Lettre du joueur au centre
                    if letter:
                        self.canvas.create_text(
                            (x1 + x2) // 2,
                            (y1 + y2) // 2 + 2,
                            text=letter,
                            font=font_letter,
                            anchor="center",
                            fill=COLOR_TEXT_DARK,
                        )

        # 2. Dessin des bordures
        # Contour exterieur
        self.canvas.create_rectangle(
            offset_x,
            offset_y,
            offset_x + grid_pixel_w,
            offset_y + grid_pixel_h,
            outline=COLOR_CELL_BLACK,
            width=2,
        )

        # Bordures verticales internes
        for r in range(self._game.height):
            for c in range(self._game.width - 1):
                bx = offset_x + (c + 1) * self._cell_size
                by1 = offset_y + r * self._cell_size
                by2 = by1 + self._cell_size

                w_left = self._game.is_white(r, c)
                w_right = self._game.is_white(r, c + 1)

                if w_left and w_right:
                    # Deux cases blanches adjacentes
                    is_dotted = (self._game.v_borders[r][c] == BORDER_DOTTED)
                    if is_dotted:
                        # Mur en pointilles pour mot compose (ex: a : priori)
                        self.canvas.create_line(
                            bx, by1 + 1, bx, by2 - 1,
                            dash=(2, 2),
                            width=2,
                            fill=COLOR_BORDER_DOTTED,
                        )
                    else:
                        self.canvas.create_line(
                            bx, by1, bx, by2,
                            fill=COLOR_BORDER_SOLID,
                            width=1,
                        )
                elif w_left != w_right:
                    # Limite avec une case noire
                    self.canvas.create_line(
                        bx, by1, bx, by2,
                        fill=COLOR_CELL_BLACK,
                        width=1,
                    )

        # Bordures horizontales internes
        for r in range(self._game.height - 1):
            for c in range(self._game.width):
                by = offset_y + (r + 1) * self._cell_size
                bx1 = offset_x + c * self._cell_size
                bx2 = bx1 + self._cell_size

                w_top = self._game.is_white(r, c)
                w_bot = self._game.is_white(r + 1, c)

                if w_top and w_bot:
                    is_dotted = (self._game.h_borders[r][c] == BORDER_DOTTED)
                    if is_dotted:
                        self.canvas.create_line(
                            bx1 + 1, by, bx2 - 1, by,
                            dash=(2, 2),
                            width=2,
                            fill=COLOR_BORDER_DOTTED,
                        )
                    else:
                        self.canvas.create_line(
                            bx1, by, bx2, by,
                            fill=COLOR_BORDER_SOLID,
                            width=1,
                        )
                elif w_top != w_bot:
                    self.canvas.create_line(
                        bx1, by, bx2, by,
                        fill=COLOR_CELL_BLACK,
                        width=1,
                    )

