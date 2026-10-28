"""Pruebas de Euler y RK2 contra resultados exactos conocidos de la ecuación lineal."""

import numpy as np
import pytest

from calculos.metodos.integradores import euler, rk2

# Ecuación de prueba u' = -k (u - a): tiene la misma forma que el Ítem 1.
K, A, U0 = 0.05, 900.0, 293.15


def f(t, u):
    return -K * (u - A)


def exacta(t):
    return A + (U0 - A) * np.exp(-K * t)


# Para la ecuación lineal, Euler multiplica el desvío por (1 - hk) en cada paso.
# Comparar con esa fórmula cerrada verifica el algoritmo paso a paso, no solo "que se parezca".
def test_euler_coincide_con_factor_de_amplificacion_exacto():
    h, n = 2.0, 30
    t, u = euler(f, U0, 0.0, h, n)
    esperado = A + (U0 - A) * (1 - h * K) ** np.arange(n + 1)
    np.testing.assert_allclose(u, esperado, rtol=1e-13)


# El RK2 del enunciado (Heun) tiene factor de amplificación 1 - hk + (hk)^2 / 2.
def test_rk2_coincide_con_factor_de_amplificacion_exacto():
    h, n = 2.0, 30
    t, u = rk2(f, U0, 0.0, h, n)
    esperado = A + (U0 - A) * (1 - h * K + (h * K) ** 2 / 2) ** np.arange(n + 1)
    np.testing.assert_allclose(u, esperado, rtol=1e-13)


def _error_final(metodo, h):
    t, u = metodo(f, U0, 0.0, h, int(round(40 / h)))
    return abs(u[-1] - exacta(t[-1]))


# El orden de convergencia es la propiedad que distingue a los métodos (Ítem 1c):
# al dividir h por 2 el error debe caer ~2 veces con Euler y ~4 veces con RK2.
@pytest.mark.parametrize("metodo, cociente", [(euler, 2.0), (rk2, 4.0)])
def test_orden_de_convergencia(metodo, cociente):
    assert _error_final(metodo, 1.0) / _error_final(metodo, 0.5) == pytest.approx(cociente, rel=0.05)


# Los tiempos devueltos deben ser exactamente t0 + k h: los parámetros de soaking
# se calculan sobre esos instantes.
def test_devuelve_n_mas_un_puntos_equiespaciados():
    t, u = rk2(f, U0, 0.0, 30.0, 50)
    assert len(t) == len(u) == 51
    np.testing.assert_allclose(np.diff(t), 30.0)


# Pasos inválidos deben rechazarse en lugar de devolver una trayectoria vacía o invertida.
@pytest.mark.parametrize("h, n", [(0.0, 10), (-1.0, 10), (1.0, 0)])
def test_rechaza_paso_o_cantidad_invalidos(h, n):
    with pytest.raises(ValueError):
        euler(f, U0, 0.0, h, n)
