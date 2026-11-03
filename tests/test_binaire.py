"""Tests du décodage des points et de l'encodage des triangles."""

import struct

import pytest

from triangulator import decoder_points, encoder_triangles

from .conftest import encoder_points, lire_triangles


@pytest.mark.parametrize(
    "points",
    [
        [(1.0, 2.0)],
        [],
        [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)],
        [(-1.0, -2.0), (-3.0, -4.0)],
        [(1.5, 2.5), (3.5, 4.5)],
    ],
    ids=["un_point", "vide", "plusieurs", "negatifs", "decimaux"],
)
def test_decodage_points_valides(points):
    """Retrouver les coordonnées dans le bon ordre."""
    assert decoder_points(encoder_points(points)) == points


@pytest.mark.parametrize(
    "donnees",
    [
        struct.pack("<I", 5) + encoder_points([(1, 2), (3, 4), (5, 6)])[4:],
        b"\x00\x00\x00",
        struct.pack("<Iff", 1, 1, 2) + b"12345678",
    ],
    ids=["points_manquants", "entete_trop_court", "octets_en_trop"],
)
def test_decodage_refuse_une_taille_incorrecte(donnees):
    """Refuser les données incomplètes ou trop longues."""
    with pytest.raises(ValueError):
        decoder_points(donnees)


@pytest.mark.parametrize(
    ("points", "triangles"),
    [
        ([(0, 0), (4, 0), (0, 3)], [(0, 1, 2)]),
        ([], []),
        ([(1, 2), (3, 4), (5, 6)], [(0, 1, 2)]),
        (
            [(0, 0), (4, 0), (0, 3), (1, 2), (3, 4), (5, 6)],
            [(0, 1, 2), (3, 4, 5)],
        ),
        ([(-1, -1), (-4, -1), (-1, -5)], [(0, 1, 2)]),
        ([(0.5, 0.5), (2.5, 0.5), (1.5, 2.5)], [(0, 1, 2)]),
    ],
    ids=[
        "nominal", "vide", "alignes", "plusieurs", "negatifs", "decimaux",
    ],
)
def test_encodage_triangles(points, triangles):
    """Vérifier la taille et le contenu du binaire."""
    donnees = encoder_triangles(points, triangles)
    assert len(donnees) == 8 + 8 * len(points) + 12 * len(triangles)
    assert lire_triangles(donnees) == (points, triangles)


def test_encodage_vide_contient_deux_compteurs():
    """Garder les deux compteurs même sans données."""
    assert encoder_triangles([], []) == b"\x00" * 8


def test_encodage_refuse_un_indice_invalide():
    """Refuser un triangle qui cite un point absent."""
    with pytest.raises(ValueError):
        encoder_triangles([(0, 0), (4, 0), (0, 3)], [(0, 1, 5)])
