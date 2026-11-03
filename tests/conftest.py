"""Données communes et client Flask utilisé par les tests."""

import struct
from unittest.mock import Mock

import pytest

from triangulator import creer_application

IDENTIFIANT = "123e4567-e89b-12d3-a456-426614174000"
CARRE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]


def encoder_points(points: list[tuple[float, float]]) -> bytes:
    """Créer un ensemble de points binaire pour les tests."""
    return struct.pack("<I", len(points)) + b"".join(
        struct.pack("<ff", x, y) for x, y in points
    )


def lire_triangles(
    donnees: bytes,
) -> tuple[list[tuple[float, float]], list[tuple[int, int, int]]]:
    """Lire les points et les triangles sans utiliser le code testé."""
    (nombre_points,) = struct.unpack_from("<I", donnees)
    debut_triangles = 4 + nombre_points * 8
    (nombre_triangles,) = struct.unpack_from("<I", donnees, debut_triangles)
    assert len(donnees) == debut_triangles + 4 + nombre_triangles * 12
    points = [
        struct.unpack_from("<ff", donnees, 4 + i * 8)
        for i in range(nombre_points)
    ]
    triangles = [
        struct.unpack_from("<III", donnees, debut_triangles + 4 + i * 12)
        for i in range(nombre_triangles)
    ]
    return points, triangles


@pytest.fixture
def manager() -> Mock:
    """PointSetManager simulé qui renvoie un carré."""
    return Mock(return_value=(200, encoder_points(CARRE)))


@pytest.fixture
def client(manager: Mock):
    """Créer un client Flask sans lancer de serveur réel."""
    application = creer_application(manager)
    application.config["TESTING"] = True
    return application.test_client()
