"""Tests simples des propriétés des triangles produits."""

import random

import pytest

from triangulator import trianguler


def aire_double(a, b, c):
    """Double de l'aire signée d'un triangle."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def verifier_triangles(points, triangles, nombre, aire_attendue):
    """Vérifier le nombre, les indices et l'aire totale."""
    assert len(triangles) == nombre
    assert set().union(*(set(t) for t in triangles)) == set(range(len(points)))
    aire_totale = 0
    for triangle in triangles:
        assert len(triangle) == 3
        assert len(set(triangle)) == 3
        assert all(0 <= indice < len(points) for indice in triangle)
        aire = abs(aire_double(*(points[i] for i in triangle))) / 2
        assert aire > 0
        aire_totale += aire
    assert aire_totale == pytest.approx(aire_attendue)


@pytest.mark.parametrize(
    ("points", "aire"),
    [
        ([(0, 0), (4, 0), (0, 3)], 6),
        ([(-1, -1), (-4, -1), (-1, -5)], 6),
        ([(0.5, 0.5), (2.5, 0.5), (1.5, 2.5)], 2),
    ],
    ids=["nominal", "negatifs", "decimaux"],
)
def test_trois_points_donnent_un_triangle(points, aire):
    """Former un triangle qui couvre toute la surface."""
    verifier_triangles(points, trianguler(points), 1, aire)


@pytest.mark.parametrize(
    "points",
    [[], [(1, 2)], [(1, 2), (3, 4)], [(1, 2), (2, 4), (3, 6)],
     [(1, 2), (1, 2), (3, 4), (0, 3)]],
    ids=["vide", "un_point", "deux_points", "alignes", "doublon"],
)
def test_points_non_triangulables_refuses(points):
    """Refuser les points insuffisants, alignés ou en double."""
    with pytest.raises(ValueError):
        trianguler(points)


@pytest.mark.parametrize(
    ("points", "nombre", "aire"),
    [
        ([(0, 0), (1, 0), (1, 1), (0, 1)], 2, 1),
        ([(0, 0), (4, 0), (0, 4), (1, 1)], 3, 8),
    ],
    ids=["carre", "point_interieur"],
)
def test_plusieurs_triangles_couvrent_la_surface(points, nombre, aire):
    """Couvrir la surface du carré ou du triangle avec point intérieur."""
    verifier_triangles(points, trianguler(points), nombre, aire)


def test_cent_points_ont_des_triangles_valides():
    """Vérifier les indices et les aires sur cent points reproductibles."""
    valeurs = random.Random(2026).sample(range(10000), 100)
    points = [divmod(valeur, 100) for valeur in valeurs]
    triangles = trianguler(points)
    assert triangles
    assert set().union(*(set(t) for t in triangles)) == set(range(len(points)))
    for triangle in triangles:
        assert len(set(triangle)) == 3
        assert all(0 <= i < len(points) for i in triangle)
        assert aire_double(*(points[i] for i in triangle)) != 0
