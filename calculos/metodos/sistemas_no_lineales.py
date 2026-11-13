"""Resolución del sistema no lineal F(T1, T2) = 0 del Ítem 5.

Esquema común: x_{k+1} = x_k - J^{-1} F(x_k). Cada método difiere en cómo arma J:
  - Newton-Raphson: jacobiano por diferencias finitas en cada iteración.
  - Secante (enunciado): J_SEC tal como figura en el enunciado.
  - Punto fijo: J constante (identidad en el enunciado).
"""

from dataclasses import dataclass, field
from typing import Callable
import numpy as np

Sistema = Callable[[np.ndarray], np.ndarray]
FabricaJ = Callable[[np.ndarray, np.ndarray], np.ndarray]

# Número de condición a partir del cual J se considera numéricamente singular.
COND_MAXIMA = 1e12


class JacobianoSingular(Exception):
    """J no se puede invertir (o está tan mal condicionado que el paso no tiene sentido)."""


@dataclass(frozen=True)
class Criterio:
    tolerancias: tuple[float, float]  # |F1| y |F2| admisibles
    max_iteraciones: int = 50
    rango_fisico: tuple[float, float] = (0.0, 1200.0)

    def cumple(self, Fx: np.ndarray) -> bool:
        return bool(np.all(np.abs(Fx) <= np.asarray(self.tolerancias)))

    def es_admisible(self, x: np.ndarray) -> bool:
        lo, hi = self.rango_fisico
        return bool(np.all(np.isfinite(x)) and np.all((x >= lo) & (x <= hi)))


@dataclass(frozen=True)
class Iteracion:
    k: int
    x: np.ndarray
    F: np.ndarray


@dataclass
class ResultadoIterativo:
    x: np.ndarray
    convergio: bool
    mensaje: str
    historial: list[Iteracion] = field(default_factory=list)
    evaluaciones: int = 0

    @property
    def iteraciones(self) -> int:
        return self.historial[-1].k if self.historial else 0


def paso_newton(J: np.ndarray, Fx: np.ndarray) -> np.ndarray:
    """Resuelve J dx = F. Lanza JacobianoSingular si J no es invertible."""
    if not np.all(np.isfinite(J)) or np.linalg.cond(J) > COND_MAXIMA:
        raise JacobianoSingular(
            f"J singular o mal condicionada:\n{np.array2string(J, precision=4)}"
        )
    return np.linalg.solve(J, Fx)


def jacobiano_diferencias(
    F: Sistema, x: np.ndarray, Fx: np.ndarray, delta: float
) -> np.ndarray:
    """J[i, j] ≈ (F_i(x + delta e_j) - F_i(x)) / delta (diferencias hacia adelante)."""
    J = np.empty((len(Fx), len(x)))
    for j in range(len(x)):
        x_mas = x.copy()
        x_mas[j] += delta
        J[:, j] = (F(x_mas) - Fx) / delta
    return J


def jacobiano_secante_enunciado(dx: np.ndarray, dF: np.ndarray) -> np.ndarray:
    """J_SEC[i, j] = ΔF_i / ΔT_j, tal como figura en el enunciado.

    Cada fila es ΔF_i · [1/ΔT1, 1/ΔT2]: las filas son proporcionales y det(J) = 0
    siempre. Se implementa igual para poder mostrarlo numéricamente en el informe.
    """
    if np.any(dx == 0):
        raise JacobianoSingular(
            "Alguna componente de ΔT es cero: J_SEC no está definida"
        )
    return np.outer(dF, 1.0 / dx)


def iterar(
    F: Sistema, x0, fabrica_J: FabricaJ, criterio: Criterio
) -> ResultadoIterativo:
    """Bucle común x_{k+1} = x_k - J^{-1} F(x_k), con historial y motivos de parada."""
    x = np.asarray(x0, float)
    res = ResultadoIterativo(x, False, "")
    for k in range(criterio.max_iteraciones + 1):
        Fx = F(x)
        res.historial.append(Iteracion(k, x.copy(), Fx.copy()))
        motivo = _motivo_parada(x, Fx, k, criterio)
        if motivo:
            res.x, res.convergio, res.mensaje = x, motivo == "Convergió", motivo
            return res
        try:
            dx = paso_newton(fabrica_J(x, Fx), Fx)
        except JacobianoSingular as error:
            res.x, res.mensaje = x, f"Se detuvo: {error}"
            return res
        x = x - dx
    return res


class _ContadorEvaluaciones:
    """Envuelve F para contar cuántas simulaciones requiere cada método."""

    def __init__(self, F: Sistema):
        self.F, self.n = F, 0

    def __call__(self, x):
        self.n += 1
        return np.asarray(self.F(np.asarray(x, float)), float)


def _ejecutar(F: Sistema, x0, crear_fabrica, criterio: Criterio) -> ResultadoIterativo:
    contador = _ContadorEvaluaciones(F)
    res = iterar(contador, x0, crear_fabrica(contador), criterio)
    res.evaluaciones = contador.n
    return res


def newton_raphson(
    F: Sistema, x0, criterio: Criterio, delta: float
) -> ResultadoIterativo:
    """J = J_NR evaluado por diferencias finitas en cada iteración."""
    return _ejecutar(
        F,
        x0,
        lambda Fc: lambda x, Fx: jacobiano_diferencias(Fc, x, Fx, delta),
        criterio,
    )


def punto_fijo(F: Sistema, x0, criterio: Criterio, J=None) -> ResultadoIterativo:
    """J constante. Por defecto J = I, como J_PF del enunciado."""
    J = np.eye(len(x0)) if J is None else np.asarray(J, float)
    return _ejecutar(F, x0, lambda Fc: lambda x, Fx: J, criterio)


def secante_enunciado(
    F: Sistema, x0, x_previo, criterio: Criterio
) -> ResultadoIterativo:
    """J = J_SEC del enunciado, armada con la iteración actual y la anterior."""

    def crear(Fc):
        previo = {"x": np.asarray(x_previo, float), "F": Fc(x_previo)}

        def fabrica(x, Fx):
            J = jacobiano_secante_enunciado(x - previo["x"], Fx - previo["F"])
            previo["x"], previo["F"] = x.copy(), Fx.copy()
            return J

        return fabrica

    return _ejecutar(F, x0, crear, criterio)


def _motivo_parada(x, Fx, k, criterio: Criterio) -> str:
    if not np.all(np.isfinite(Fx)):
        return "Se detuvo: F no es finita"
    if criterio.cumple(Fx):
        return "Convergió"
    if not criterio.es_admisible(x):
        return "Se detuvo: la iteración salió del rango físico admisible"
    if k == criterio.max_iteraciones:
        return "No convergió en el máximo de iteraciones"
    return ""
