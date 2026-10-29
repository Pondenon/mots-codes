"""
encoder.py
----------
Attribue les codes numeriques (1 a 26) aux lettres de l'alphabet
et prepare la grille codee pour le joueur avec les indices de depart.
"""

from dataclasses import dataclass
import random
import string
from typing import Optional

from core.grid_generator import GeneratedGrid
from utils.config import NUM_CODES, NUM_HINTS, CELL_WHITE


@dataclass
class EncodedPuzzle:
    """Structure contenant toutes les donnees du puzzle encode."""
    grid: GeneratedGrid
    letter_to_code: dict[str, int]
    code_to_letter: dict[int, str]
    encoded_grid: list[list[Optional[int]]]
    initial_hints: dict[int, str]


class PuzzleEncoder:
    """
    Encodeur de grille pour le jeu Les Mots Codes.
    Associe chaque lettre de A a Z a un entier unique entre 1 et 26.
    """

    @staticmethod
    def encode(
        grid: GeneratedGrid,
        num_hints: int = NUM_HINTS,
    ) -> EncodedPuzzle:
        """
        Encode une grille generee et selectionne les indices de depart.

        Parameters
        ----------
        grid :
            Grille generee par GridGenerator.
        num_hints :
            Nombre de lettres a reveler au joueur au debut.

        Returns
        -------
        EncodedPuzzle contenant les correspondances et la grille chiffree.
        """
        alphabet = list(string.ascii_uppercase)
        numbers = list(range(1, NUM_CODES + 1))
        random.shuffle(numbers)

        letter_to_code: dict[str, int] = {}
        code_to_letter: dict[int, str] = {}

        for letter, code in zip(alphabet, numbers):
            letter_to_code[letter] = code
            code_to_letter[code] = letter

        # Construction de la grille encodee (chiffres pour cases blanches, None pour noires)
        encoded_grid: list[list[Optional[int]]] = [
            [None for _ in range(grid.width)] for _ in range(grid.height)
        ]

        for r in range(grid.height):
            for c in range(grid.width):
                if grid.is_white(r, c):
                    letter = grid.get_letter(r, c)
                    if letter is not None:
                        encoded_grid[r][c] = letter_to_code[letter]

        # Selection des indices de depart
        # On choisit parmi les lettres qui apparaissent effectivement dans la grille
        available_letters = sorted(grid.unique_letters)
        hints_count = min(num_hints, len(available_letters))

        # Favoriser les lettres qui ont une bonne frequence d'apparition
        # pour offrir un point de depart interessant au joueur
        frequencies: dict[str, int] = {}
        for r in range(grid.height):
            for c in range(grid.width):
                let = grid.get_letter(r, c)
                if let:
                    frequencies[let] = frequencies.get(let, 0) + 1

        # Trier les lettres par frequence decroissante et en choisir parmi les plus frequentes
        sorted_by_freq = sorted(
            available_letters,
            key=lambda l: frequencies.get(l, 0),
            reverse=True
        )

        chosen_letters: list[str] = []
        if sorted_by_freq:
            # Prendre la lettre la plus frequente
            chosen_letters.append(sorted_by_freq[0])
            # Prendre d'autres lettres parmi les frequences moyennes
            remaining = sorted_by_freq[1:]
            random.shuffle(remaining)
            chosen_letters.extend(remaining[: hints_count - 1])

        initial_hints: dict[int, str] = {
            letter_to_code[l]: l for l in chosen_letters
        }

        return EncodedPuzzle(
            grid=grid,
            letter_to_code=letter_to_code,
            code_to_letter=code_to_letter,
            encoded_grid=encoded_grid,
            initial_hints=initial_hints,
        )

