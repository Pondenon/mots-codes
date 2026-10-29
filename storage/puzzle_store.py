"""
puzzle_store.py
---------------
Gestionnaire de persistance pour sauvegarder, charger et lister
les puzzles generes et les parties en cours en format JSON.
"""

import json
from pathlib import Path
from typing import Optional

from core.game_model import GameModel
from utils.config import PUZZLES_DIR


class PuzzleStore:
    """
    Gestionnaire de stockage des puzzles dans le dossier de la langue active.
    """

    def __init__(self, puzzles_dir: Path = PUZZLES_DIR) -> None:
        self.puzzles_dir = puzzles_dir
        self.puzzles_dir.mkdir(parents=True, exist_ok=True)

    def save_puzzle(self, game: GameModel) -> Path:
        """
        Sauvegarde une partie au format JSON.

        Parameters
        ----------
        game :
            Instance de GameModel a persister.

        Returns
        -------
        Path du fichier JSON cree ou mis a jour.
        """
        filepath = self.puzzles_dir / f"{game.puzzle_id}.json"
        data = game.to_dict()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def load_puzzle(self, puzzle_id: str) -> Optional[GameModel]:
        """
        Charge un puzzle depuis son identifiant ou son nom de fichier.

        Parameters
        ----------
        puzzle_id :
            Identifiant du puzzle (avec ou sans l'extension .json).

        Returns
        -------
        Instance GameModel reconstituee, ou None si le fichier n'existe pas.
        """
        if not puzzle_id.endswith(".json"):
            filename = f"{puzzle_id}.json"
        else:
            filename = puzzle_id

        filepath = self.puzzles_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return GameModel.from_dict(data)
        except Exception:
            return None

    def list_puzzles(self) -> list[dict]:
        """
        Retourne la liste des metadonnees de tous les puzzles sauvegardes,
        tries du plus recent au plus ancien.

        Returns
        -------
        Liste de dictionnaires contenant id, date, taille, temps, statut.
        """
        puzzles = []

        for filepath in self.puzzles_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                puzzles.append({
                    "puzzle_id": data.get("puzzle_id", filepath.stem),
                    "created_at": data.get("created_at", ""),
                    "width": data.get("width", 0),
                    "height": data.get("height", 0),
                    "elapsed_seconds": data.get("elapsed_seconds", 0),
                    "is_completed": data.get("is_completed", False),
                    "is_paused": data.get("is_paused", False),
                })
            except Exception:
                continue

        puzzles.sort(key=lambda p: p.get("created_at", ""), reverse=True)
        return puzzles

    def delete_puzzle(self, puzzle_id: str) -> bool:
        """
        Supprime le fichier d'un puzzle donne.

        Returns
        -------
        True si supprime avec succes, False sinon.
        """
        if not puzzle_id.endswith(".json"):
            filename = f"{puzzle_id}.json"
        else:
            filename = puzzle_id

        filepath = self.puzzles_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False
