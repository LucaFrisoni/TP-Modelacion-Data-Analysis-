"""Formato de resultados numéricos para tablas del informe (cifras significativas)."""

import math


def redondear_cifras(x: float, cifras: int = 3) -> float:
    """Redondea x a `cifras` cifras significativas (597.71 -> 598, 0.012345 -> 0.0123)."""
    if cifras < 1:
        raise ValueError("Se necesita al menos una cifra significativa")
    if x == 0 or not math.isfinite(x):
        return x
    return round(x, cifras - 1 - math.floor(math.log10(abs(x))))


def texto_cifras(x: float, cifras: int = 3) -> str:
    """Igual que redondear_cifras pero como texto sin notación científica ni '.0' sobrante."""
    r = redondear_cifras(x, cifras)
    if r == 0 or not math.isfinite(r):
        return str(r)
    decimales = max(0, cifras - 1 - math.floor(math.log10(abs(r))))
    return f"{r:.{decimales}f}"
