"""
game_model.py
-------------
Modele d'etat pour une partie de jeu Les Mots Codes.
Centralise l'etat du puzzle, les reponses du joueur, le chronometre
et les verifications de victoire.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Optional

from core.encoder import EncodedPuzzle
from utils.config import CELL_WHITE, CELL_BLACK


@dataclass
class GameModel:
    """
    Representation complete d'une partie en cours ou terminee.
    """
    puzzle_id: str
    created_at: str
    width: int
    height: int
    solution: list[list[Optional[str]]]
    cell_types: list[list[str]]
    v_borders: list[list[str]]
    h_borders: list[list[str]]
    letter_to_code: dict[str, int]
    code_to_letter: dict[int, str]
    encoded_grid: list[list[Optional[int]]]
    initial_hints: dict[int, str]
    player_mapping: dict[int, str] = field(default_factory=dict)
    elapsed_seconds: int = 0
    is_paused: bool = False
    is_completed: bool = False
    num_codes: int = 26

    @classmethod
    def new_game(
        cls,
        puzzle: EncodedPuzzle,
        puzzle_id: Optional[str] = None,
    ) -> "GameModel":
        """
        Initialise une nouvelle partie a partir d'un EncodedPuzzle.
        """
        if puzzle_id is None:
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            short_id = uuid.uuid4().hex[:6]
            puzzle_id = f"puzzle_{now_str}_{short_id}"

        initial_mapping = dict(puzzle.initial_hints)

        game = cls(
            puzzle_id=puzzle_id,
            created_at=datetime.now().isoformat(),
            width=puzzle.grid.width,
            height=puzzle.grid.height,
            solution=puzzle.grid.solution,
            cell_types=puzzle.grid.cell_types,
            v_borders=puzzle.grid.v_borders,
            h_borders=puzzle.grid.h_borders,
            letter_to_code=puzzle.letter_to_code,
            code_to_letter=puzzle.code_to_letter,
            encoded_grid=puzzle.encoded_grid,
            initial_hints=dict(puzzle.initial_hints),
            player_mapping=initial_mapping,
            elapsed_seconds=0,
            is_paused=False,
            is_completed=False,
            num_codes=puzzle.num_codes,
        )
        return game

    def is_white(self, row: int, col: int) -> bool:
        """Retourne True si la case est une case blanche contenant une lettre."""
        return (
            0 <= row < self.height
            and 0 <= col < self.width
            and self.cell_types[row][col] == CELL_WHITE
        )

    def get_code(self, row: int, col: int) -> Optional[int]:
        """Retourne le code numerique de la case blanche ou None."""
        if not self.is_white(row, col):
            return None
        return self.encoded_grid[row][col]

    def get_player_letter(self, row: int, col: int) -> Optional[str]:
        """Retourne la lettre actuellement devinee pour cette case par le joueur."""
        code = self.get_code(row, col)
        if code is None:
            return None
        return self.player_mapping.get(code)

    def get_expected_letter(self, row: int, col: int) -> Optional[str]:
        """Retourne la lettre de solution attendue a cette case."""
        if not self.is_white(row, col):
            return None
        return self.solution[row][col]

    def is_hint(self, code: int) -> bool:
        """Retourne True si ce code fait partie des indices donnes d'office."""
        return code in self.initial_hints

    def set_letter_for_code(self, code: int, letter: Optional[str]) -> bool:
        """
        Associe une lettre a un code chiffre (ou supprime l'association si None).
        Ne modifie pas les indices d'office.
        """
        if self.is_completed:
            return False

        if self.is_hint(code):
            return False

        if letter:
            clean_letter = letter.strip().upper()
            if len(clean_letter) == 1 and clean_letter.isalpha():
                self.player_mapping[code] = clean_letter
            else:
                return False
        else:
            self.player_mapping.pop(code, None)

        return self.check_completion()

    def check_completion(self) -> bool:
        """
        Verifie si l'integralite des cases blanches est remplie
        avec la lettre correcte de la solution.
        """
        for r in range(self.height):
            for c in range(self.width):
                if self.is_white(r, c):
                    expected = self.solution[r][c]
                    code = self.encoded_grid[r][c]
                    if code is None:
                        return False
                    actual = self.player_mapping.get(code)
                    if actual != expected:
                        return False

        self.is_completed = True
        return True

    def toggle_pause(self) -> bool:
        """Inverse l'etat de pause et retourne le nouvel etat."""
        if not self.is_completed:
            self.is_paused = not self.is_paused
        return self.is_paused

    def tick(self) -> int:
        """Incremente le chronometre d'une seconde si la partie est active."""
        if not self.is_paused and not self.is_completed:
            self.elapsed_seconds += 1
        return self.elapsed_seconds

    def to_dict(self) -> dict:
        """Convertit l'etat du jeu en dictionnaire serialisable en JSON."""
        return {
            "puzzle_id": self.puzzle_id,
            "created_at": self.created_at,
            "width": self.width,
            "height": self.height,
            "solution": self.solution,
            "cell_types": self.cell_types,
            "v_borders": self.v_borders,
            "h_borders": self.h_borders,
            "letter_to_code": self.letter_to_code,
            "code_to_letter": {str(k): v for k, v in self.code_to_letter.items()},
            "encoded_grid": self.encoded_grid,
            "initial_hints": {str(k): v for k, v in self.initial_hints.items()},
            "player_mapping": {str(k): v for k, v in self.player_mapping.items()},
            "elapsed_seconds": self.elapsed_seconds,
            "is_paused": self.is_paused,
            "is_completed": self.is_completed,
            "num_codes": self.num_codes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameModel":
        """Reconstitue une instance GameModel depuis un dictionnaire JSON."""
        letter_to_code = data["letter_to_code"]
        num_codes = data.get("num_codes", len(letter_to_code))

        return cls(
            puzzle_id=data["puzzle_id"],
            created_at=data["created_at"],
            width=data["width"],
            height=data["height"],
            solution=data["solution"],
            cell_types=data["cell_types"],
            v_borders=data["v_borders"],
            h_borders=data["h_borders"],
            letter_to_code=letter_to_code,
            code_to_letter={int(k): v for k, v in data["code_to_letter"].items()},
            encoded_grid=data["encoded_grid"],
            initial_hints={int(k): v for k, v in data["initial_hints"].items()},
            player_mapping={int(k): v for k, v in data["player_mapping"].items()},
            elapsed_seconds=data.get("elapsed_seconds", 0),
            is_paused=data.get("is_paused", False),
            is_completed=data.get("is_completed", False),
            num_codes=num_codes,
        )
