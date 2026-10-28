"""Métodos de Euler explícito y Runge-Kutta 2 tal como los define el enunciado (pág. 9)."""

from typing import Callable

import numpy as np

Derivada = Callable[[float, float], float]


def _validar(h: float, n_pasos: int):
    if h <= 0:
        raise ValueError(f"El paso h debe ser positivo (se recibió {h})")
    if n_pasos < 1:
        raise ValueError(f"Se necesita al menos un paso (se recibió {n_pasos})")


def euler(f: Derivada, u0: float, t0: float, h: float, n_pasos: int):
    """u_{n+1} = u_n + h f(u_n, t_n). Devuelve (t, u) con n_pasos + 1 puntos."""
    _validar(h, n_pasos)
    t = t0 + h * np.arange(n_pasos + 1)
    u = np.empty(n_pasos + 1)
    u[0] = u0
    for n in range(n_pasos):
        u[n + 1] = u[n] + h * f(t[n], u[n])
    return t, u


def rk2(f: Derivada, u0: float, t0: float, h: float, n_pasos: int):
    """q1 = h f(u_n, t_n); q2 = h f(u_n + q1, t_{n+1}); u_{n+1} = u_n + (q1 + q2) / 2."""
    _validar(h, n_pasos)
    t = t0 + h * np.arange(n_pasos + 1)
    u = np.empty(n_pasos + 1)
    u[0] = u0
    for n in range(n_pasos):
        q1 = h * f(t[n], u[n])
        q2 = h * f(t[n + 1], u[n] + q1)
        u[n + 1] = u[n] + 0.5 * (q1 + q2)
    return t, u


METODOS = {"euler": euler, "rk2": rk2}
