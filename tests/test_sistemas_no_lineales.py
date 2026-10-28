"""Pruebas de los métodos para sistemas no lineales sobre sistemas con solución conocida."""

import numpy as np
import pytest

from calculos.metodos import sistemas_no_lineales as cal

# Sistema de prueba con solución (2, 1): x^2 - y - 3 = 0 y x + y^2 - 3 = 0.
SOLUCION = np.array([2.0, 1.0])
CRITERIO = cal.Criterio(tolerancias=(1e-10, 1e-10), max_iteraciones=50, rango_fisico=(-10, 10))


def F(x):
    return np.array([x[0] ** 2 - x[1] - 3, x[0] + x[1] ** 2 - 3])


# Newton con jacobiano por diferencias finitas debe converger a la raíz en pocas iteraciones.
def test_newton_converge_a_la_solucion_conocida():
    r = cal.newton_raphson(F, [1.5, 1.5], CRITERIO, delta=1e-6)
    assert r.convergio and r.iteraciones <= 8
    np.testing.assert_allclose(r.x, SOLUCION, atol=1e-8)


# La secante multivariable (Broyden) es la alternativa propuesta a la J_SEC del enunciado.
def test_broyden_converge_a_la_solucion_conocida():
    r = cal.secante_broyden(F, [1.5, 1.5], CRITERIO, delta=1e-6)
    assert r.convergio
    np.testing.assert_allclose(r.x, SOLUCION, atol=1e-8)


# Hallazgo clave para el informe: J_SEC del enunciado tiene filas proporcionales,
# así que su determinante es cero para cualquier par de iteraciones.
def test_jacobiano_secante_del_enunciado_es_siempre_singular():
    rng = np.random.default_rng(0)
    for _ in range(20):
        J = cal.jacobiano_secante_enunciado(rng.normal(size=2), rng.normal(size=2))
        assert abs(np.linalg.det(J)) < 1e-12 * max(1.0, np.abs(J).max() ** 2)


# El método debe informar el problema y detenerse, en lugar de producir números sin sentido.
def test_secante_del_enunciado_se_detiene_informando_singularidad():
    r = cal.secante_enunciado(F, [1.5, 1.5], [1.4, 1.3], CRITERIO)
    assert not r.convergio and "singular" in r.mensaje


# Con J constante, punto fijo converge si la iteración es contractiva (J cercana a la real).
def test_punto_fijo_converge_con_J_constante_adecuada():
    J = cal.jacobiano_diferencias(F, SOLUCION, F(SOLUCION), 1e-6)
    r = cal.punto_fijo(F, [2.2, 0.8], CRITERIO, J)
    assert r.convergio
    np.testing.assert_allclose(r.x, SOLUCION, atol=1e-8)


# Si una iteración sale del rango físico admisible, debe detenerse y decirlo.
def test_detiene_al_salir_del_rango_fisico():
    crit = cal.Criterio((1e-10, 1e-10), 50, rango_fisico=(0.0, 3.0))
    r = cal.punto_fijo(F, [1.5, 1.5], crit)  # J = I diverge en este sistema
    assert not r.convergio and "rango físico" in r.mensaje


# El amortiguamiento solo acepta pasos que reducen el residuo: el residuo final
# nunca puede ser peor que el inicial.
def test_amortiguado_no_empeora_el_residuo():
    crit = cal.Criterio((1e-10, 1e-10), 5, (-10, 10), amortiguado=True)
    r = cal.punto_fijo(F, [1.5, 1.5], crit)
    residuos = [crit.residuo(it.F) for it in r.historial]
    assert residuos[-1] <= residuos[0]


# El conteo de simulaciones permite comparar el costo de los métodos en el informe.
def test_cuenta_evaluaciones_de_F():
    r = cal.newton_raphson(F, [1.5, 1.5], CRITERIO, delta=1e-6)
    assert r.evaluaciones == 3 * r.iteraciones + 1  # F(x) + 2 columnas por iteración
