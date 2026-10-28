"""Parámetros metalúrgicos de salida (Ítem 2c): tiempo de soaking Sk y temperatura Tsk.
Se calculan directamente sobre los puntos de la simulación, en °C y minutos.
"""

from dataclasses import dataclass
import numpy as np
from calculos.datos import enunciado as E

CONVENCIONES_SK = ("intervalos", "puntos")

# Margen para incluir en la banda puntos que caen sobre el borde por redondeo.
_TOL_BANDA_C = 1e-9


@dataclass(frozen=True)
class Soaking:
    sk_min: float
    tsk_C: float
    T_final_C: float
    en_banda: np.ndarray  # máscara booleana de los puntos dentro de la banda

    @property
    def limite_inferior_C(self) -> float:
        return self.T_final_C - E.ANCHO_BANDA_SOAKING_C


def puntos_en_banda(T_C: np.ndarray, ancho_C: float) -> np.ndarray:
    """Máscara de los puntos con T dentro de [T_final - ancho, T_final]."""
    T_final = T_C[-1]
    return (T_C >= T_final - ancho_C - _TOL_BANDA_C) & (T_C <= T_final + _TOL_BANDA_C)


def tiempo_acumulado_min(
    t_min: np.ndarray, en_banda: np.ndarray, convencion: str
) -> float:
    """Convierte los puntos en banda en un tiempo acumulado.

    TODO: VALIDAR FÓRMULA O CRITERIO — la convención la define el equipo
    (CONVENCION_SK en calculos/datos/decisiones.py).
      "intervalos": suma de los intervalos con ambos extremos en la banda.
      "puntos":     cantidad de puntos en banda por el paso de tiempo.
    """
    if convencion == "intervalos":
        ambos = en_banda[:-1] & en_banda[1:]
        return float(np.sum(np.diff(t_min)[ambos]))
    if convencion == "puntos":
        return float(np.count_nonzero(en_banda) * np.mean(np.diff(t_min)))
    raise ValueError(
        f"Convención {convencion!r} desconocida. Opciones: {CONVENCIONES_SK}"
    )


def calcular_soaking(t_min, T_C, convencion: str) -> Soaking:
    """Sk = tiempo acumulado en la banda; Tsk = promedio de T en los puntos de la banda.

    TODO: VALIDAR FÓRMULA O CRITERIO — Tsk se toma como media aritmética de los
    puntos en banda (con paso uniforme, equivale a un promedio temporal simple).
    """
    t_min, T_C = np.asarray(t_min, float), np.asarray(T_C, float)
    if len(t_min) != len(T_C) or len(T_C) < 2:
        raise ValueError("Se necesitan al menos dos puntos con t y T del mismo largo")
    en_banda = puntos_en_banda(T_C, E.ANCHO_BANDA_SOAKING_C)
    sk = tiempo_acumulado_min(t_min, en_banda, convencion)
    return Soaking(sk, float(np.mean(T_C[en_banda])), float(T_C[-1]), en_banda)
