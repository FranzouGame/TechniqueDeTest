"""Tests de l'API avec le client Flask et un faux PointSetManager."""

import struct
from unittest.mock import Mock

import pytest

from .conftest import CARRE, IDENTIFIANT, encoder_points, lire_triangles


def verifier_erreur(reponse, statut):
    """Vérifier le statut et les deux champs JSON obligatoires."""
    assert reponse.status_code == statut
    assert reponse.mimetype == "application/json"
    contenu = reponse.get_json()
    assert isinstance(contenu.get("code"), str) and contenu["code"]
    assert isinstance(contenu.get("message"), str) and contenu["message"]


def test_api_renvoie_deux_triangles(client, manager: Mock):
    """Lire la réponse binaire d'une requête sur un carré."""
    reponse = client.get(f"/triangulation/{IDENTIFIANT}")
    assert reponse.status_code == 200
    assert reponse.mimetype == "application/octet-stream"
    points, triangles = lire_triangles(reponse.data)
    assert points == CARRE
    assert len(triangles) == 2
    manager.assert_called_once_with(IDENTIFIANT)


def test_api_refuse_un_mauvais_identifiant(client, manager: Mock):
    """Refuser l'identifiant avant d'appeler le manager."""
    verifier_erreur(client.get("/triangulation/pas-un-uuid"), 400)
    manager.assert_not_called()


@pytest.mark.parametrize(
    ("statut_manager", "statut_attendu"),
    [(404, 404), (503, 503), (500, 503)],
    ids=["absent", "indisponible", "erreur_interne"],
)
def test_api_reagit_aux_erreurs_du_manager(
    client, manager: Mock, statut_manager, statut_attendu
):
    """Renvoyer le bon statut quand le manager échoue."""
    manager.return_value = (statut_manager, b"")
    verifier_erreur(client.get(f"/triangulation/{IDENTIFIANT}"), statut_attendu)
    manager.assert_called_once_with(IDENTIFIANT)


@pytest.mark.parametrize("erreur", [ConnectionError("panne"), TimeoutError("delai")])
def test_api_reagit_aux_pannes_reseau(client, manager: Mock, erreur):
    """Renvoyer 503 sans afficher le détail de la panne."""
    manager.side_effect = erreur
    reponse = client.get(f"/triangulation/{IDENTIFIANT}")
    verifier_erreur(reponse, 503)
    assert str(erreur) not in reponse.get_json()["message"]


@pytest.mark.parametrize(
    "donnees",
    [
        struct.pack("<I", 5) + encoder_points([(1, 2), (3, 4), (5, 6)])[4:],
        encoder_points([(1, 2), (3, 4)]),
        encoder_points([]),
    ],
    ids=["binaire_invalide", "deux_points", "vide"],
)
def test_api_refuse_des_points_inutilisables(client, manager: Mock, donnees):
    """Renvoyer une erreur JSON si les points sont invalides."""
    manager.return_value = (200, donnees)
    verifier_erreur(client.get(f"/triangulation/{IDENTIFIANT}"), 500)


def test_api_refuse_post(client):
    """N'autoriser que GET sur cette route."""
    assert client.post(f"/triangulation/{IDENTIFIANT}").status_code == 405


@pytest.mark.parametrize("chemin", ["/triangulation/", "/inconnu"])
def test_api_refuse_une_route_inconnue(client, chemin):
    """Renvoyer 404 si la route ou l'identifiant manque."""
    assert client.get(chemin).status_code == 404
