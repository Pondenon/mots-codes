"""
main.py
-------
Point d'entree principal de l'application Les Mots Codes.
Verifie la disponibilite du dictionnaire et demarre l'interface graphique.
"""

import sys
from utils.config import DB_PATH, CURRENT_LANGUAGE


def check_prerequisites() -> bool:
    """Verifie que la base de donnees du dictionnaire a ete generee."""
    if not DB_PATH.exists():
        print(f"Erreur : La base de donnees est introuvable : {DB_PATH}")
        print("Veuillez d'abord executer les scripts de preparation :")
        print("  1. python3 tools/build_raw_wordlist.py")
        print(f"  2. python3 tools/setup_dictionary.py --lang {CURRENT_LANGUAGE}")
        return False
    return True


def main() -> None:
    """Lance l'application Les Mots Codes."""
    if not check_prerequisites():
        sys.exit(1)

    from ui.app import MotsCodesApp

    app = MotsCodesApp()
    app.mainloop()


if __name__ == "__main__":
    main()

