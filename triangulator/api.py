"""Squelette de l'API Flask avec un PointSetManager simulable."""

from collections.abc import Callable

from flask import Flask

RecupererPoints = Callable[[str], tuple[int, bytes]]


def creer_application(recuperer_points: RecupererPoints) -> Flask:
    """Créer l'application avec une fonction qui récupère les points.

    Cette fonction reçoit un UUID et renvoie un statut HTTP et un corps binaire.
    Elle peut lever OSError en cas de panne réseau.
    """
    application = Flask(__name__)

    @application.get("/triangulation/<identifiant>")
    def obtenir_triangulation(identifiant: str) -> bytes:
        """Répondre à une demande de triangulation."""
        raise NotImplementedError("Route de triangulation non implémentée")

    return application
