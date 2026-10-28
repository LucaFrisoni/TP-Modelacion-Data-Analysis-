"""Calor específico C(T): tablas del enunciado, valor promedio y ajuste polinómico.

Las tablas están en °C, así que las funciones C(T) de este módulo reciben T en °C.
"""

from typing import Callable

import numpy as np

from calculos.datos import enunciado as E
from calculos.metodos.minimos_cuadrados import AjustePolinomico, ajustar, ajustes_hasta_interpolante

FuncionCalor = Callable[[float], float]


def tabla(nombre: str) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve (T [°C], C [J/kg K]) de la tabla indicada."""
    if nombre not in E.TABLAS_C:
        raise ValueError(f"Tabla {nombre!r} inexistente. Opciones: {sorted(E.TABLAS_C)}")
    return np.array(E.TEMPERATURAS_TABLA_C), np.array(E.TABLAS_C[nombre])


def promedio_tabla(nombre: str) -> float:
    """C promedio: media aritmética de los 7 valores tabulados.

    TODO: VALIDAR FÓRMULA O CRITERIO — interpretación de "valor promedio de la tabla".
    """
    return float(np.mean(tabla(nombre)[1]))


def calor_constante(c: float) -> FuncionCalor:
    """C(T) constante, para los Ítems 1 y 2b."""
    if c <= 0:
        raise ValueError("El calor específico debe ser positivo")
    return lambda T_C: c


def ajuste_tabla(nombre: str, grado: int) -> AjustePolinomico:
    """C(T) por mínimos cuadrados del grado indicado (T en °C)."""
    return ajustar(*tabla(nombre), grado)


def todos_los_ajustes(nombre: str) -> list[AjustePolinomico]:
    """Ajustes de grado 0 hasta el interpolante, para elegir el grado (Ítem 2a)."""
    return ajustes_hasta_interpolante(*tabla(nombre))
