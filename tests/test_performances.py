"""Mesures de temps et de mémoire, séparées des autres tests."""

import random
import statistics
import time
import tracemalloc
from functools import partial
from unittest.mock import Mock

import pytest

from triangulator import decoder_points, encoder_triangles, trianguler

from .conftest import IDENTIFIANT, encoder_points

pytestmark = pytest.mark.perf


def mesurer(operation):
    """Renvoyer la médiane de trois mesures en secondes."""
    durees = []
    for _ in range(3):
        debut = time.perf_counter()
        operation()
        durees.append(time.perf_counter() - debut)
    return statistics.median(durees)


def points_aleatoires(nombre):
    """Créer des points distincts et reproductibles."""
    valeurs = random.Random(2026).sample(range(400 * 400), nombre)
    return [divmod(valeur, 400) for valeur in valeurs]


@pytest.mark.parametrize("nombre", [1000, 10000, 100000])
def test_temps_decodage(nombre):
    """Mesurer le décodage de trois tailles d'entrée."""
    points = [(float(i), float(i % 97)) for i in range(nombre)]
    donnees = encoder_points(points)
    duree = mesurer(lambda: decoder_points(donnees))
    print(f"décodage {nombre} : {duree:.4f} s")
    if nombre == 100000:
        assert duree < 1


@pytest.mark.parametrize("nombre", [1000, 10000, 100000])
def test_temps_encodage(nombre):
    """Mesurer l'encodage de trois tailles d'entrée."""
    points = [(float(i), float(i % 97)) for i in range(nombre)]
    triangles = [(0, i, i + 1) for i in range(1, nombre - 1)]
    duree = mesurer(lambda: encoder_triangles(points, triangles))
    print(f"encodage {nombre} : {duree:.4f} s")
    if nombre == 100000:
        assert duree < 1


def test_temps_aller_retour():
    """Mesurer les deux conversions et vérifier les points obtenus."""
    points = [(float(i), float(i % 101)) for i in range(10000)]
    taille_points = len(encoder_points(points))

    def aller_retour():
        donnees = encoder_triangles(points, [])
        return decoder_points(donnees[:taille_points])

    duree = mesurer(aller_retour)
    assert aller_retour() == points
    print(f"aller-retour 10000 : {duree:.4f} s")


@pytest.mark.parametrize("nombre", [100, 1000, 10000])
def test_temps_triangulation(nombre):
    """Mesurer la triangulation de trois tailles d'entrée."""
    points = points_aleatoires(nombre)
    duree = mesurer(lambda: trianguler(points))
    print(f"triangulation {nombre} : {duree:.4f} s")
    if nombre == 10000:
        assert duree < 10


def test_evolution_du_temps():
    """Comparer les temps quand le nombre de points double."""
    durees = []
    for nombre in (1000, 2000, 4000):
        points = points_aleatoires(nombre)
        durees.append(mesurer(partial(trianguler, points)))
    print(f"évolution : {durees}")
    assert durees[1] <= 4 * durees[0]
    assert durees[2] <= 4 * durees[1]


def test_temps_requete_complete(client, manager: Mock):
    """Mesurer une requête avec dix mille points renvoyés par le manager."""
    manager.return_value = (200, encoder_points(points_aleatoires(10000)))

    def requete():
        reponse = client.get(f"/triangulation/{IDENTIFIANT}")
        assert reponse.status_code == 200

    duree = mesurer(requete)
    print(f"requête complète 10000 : {duree:.4f} s")
    assert duree < 10


def test_memoire_decodage():
    """Limiter la mémoire utilisée pour décoder cent mille points."""
    donnees = encoder_points([(float(i), float(i % 97)) for i in range(100000)])
    tracemalloc.start()
    try:
        points = decoder_points(donnees)
        _, maximum = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert len(points) == 100000
    print(f"mémoire de décodage : {maximum / 1048576:.1f} Mio")
    assert maximum < 80 * 1048576


def test_points_groupes_et_repartis():
    """Comparer la durée sur des points groupés et répartis."""
    repartis = points_aleatoires(1000)
    groupes = [(x / 1000, y / 1000) for x, y in repartis]
    duree_repartis = mesurer(lambda: trianguler(repartis))
    duree_groupes = mesurer(lambda: trianguler(groupes))
    print(f"répartis : {duree_repartis:.4f} s ; groupés : {duree_groupes:.4f} s")
    assert duree_groupes < 4 * duree_repartis
