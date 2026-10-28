"""Ajuste polinómico por mínimos cuadrados resolviendo las ecuaciones normales."""

from dataclasses import dataclass

import numpy as np
from numpy.polynomial import Polynomial


@dataclass(frozen=True)
class AjustePolinomico:
    """Polinomio de mínimos cuadrados (internamente en la variable escalada z ∈ [-1, 1])."""

    grado: int
    polinomio: Polynomial
    suma_cuadrados_residuos: float
    n_puntos: int

    def __call__(self, x):
        return self.polinomio(x)

    @property
    def rmse(self) -> float:
        return float(np.sqrt(self.suma_cuadrados_residuos / self.n_puntos))

    def coeficientes(self) -> np.ndarray:
        """Coeficientes a0..an de p(x) = a0 + a1 x + ... en la variable original (para el informe)."""
        return self.polinomio.convert().coef


def ajustar(x, y, grado: int) -> AjustePolinomico:
    """Resuelve (A^T A) a = A^T y con A de Vandermonde.

    Se trabaja en z = (x - centro) / semiancho ∈ [-1, 1] para que la matriz normal
    esté bien condicionada (con x hasta 800 y grado 6 no lo estaría).
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    if not 0 <= grado <= len(x) - 1:
        raise ValueError(f"El grado debe estar entre 0 y {len(x) - 1} (polinomio interpolante)")
    dominio = [x.min(), x.max()]
    centro, semiancho = (dominio[0] + dominio[1]) / 2, (dominio[1] - dominio[0]) / 2
    A = np.vander((x - centro) / semiancho, grado + 1, increasing=True)
    coef = np.linalg.solve(A.T @ A, A.T @ y)
    residuos = A @ coef - y
    polinomio = Polynomial(coef, domain=dominio, window=[-1, 1])
    return AjustePolinomico(grado, polinomio, float(residuos @ residuos), len(x))


def ajustes_hasta_interpolante(x, y) -> list[AjustePolinomico]:
    """Todos los ajustes desde grado 0 hasta el interpolante (grado n - 1)."""
    return [ajustar(x, y, g) for g in range(len(x))]
