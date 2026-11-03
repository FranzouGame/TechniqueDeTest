"""Interfaces du format binaire et du calcul géométrique."""

Point = tuple[float, float]
Triangle = tuple[int, int, int]


def decoder_points(donnees: bytes) -> list[Point]:
    """Décoder un ensemble de points binaire."""
    raise NotImplementedError("Décodage des points non implémenté")


def trianguler(points: list[Point]) -> list[Triangle]:
    """Renvoyer les triangles sous forme d'indices de points."""
    raise NotImplementedError("Triangulation non implémentée")


def encoder_triangles(points: list[Point], triangles: list[Triangle]) -> bytes:
    """Encodage des points et des indices des triangles."""
    raise NotImplementedError("Encodage des triangles non implémenté")
