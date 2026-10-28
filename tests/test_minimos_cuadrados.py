"""Pruebas del ajuste por mínimos cuadrados de C(T) y del promedio de la tabla."""

import numpy as np
import pytest

from calculos.metodos.minimos_cuadrados import ajustar, ajustes_hasta_interpolante
from calculos.modelo.calor_especifico import promedio_tabla, tabla


# Con 7 puntos, el ajuste de grado 6 es el polinomio interpolante: debe pasar
# exactamente por todos los puntos de la tabla (lo pide el Ítem 2a).
@pytest.mark.parametrize("nombre", ["A", "B", "C", "D"])
def test_grado_maximo_interpola_la_tabla(nombre):
    T, C = tabla(nombre)
    ajuste = ajustar(T, C, len(T) - 1)
    np.testing.assert_allclose(ajuste(T), C, rtol=1e-9)
    assert ajuste.suma_cuadrados_residuos == pytest.approx(0.0, abs=1e-12)


# El ajuste de grado 0 por mínimos cuadrados es la media: une el Ítem 2a con el C promedio
# del Ítem 1. Para la tabla B del grupo: 3730 / 7.
def test_grado_cero_es_el_promedio_de_la_tabla():
    T, C = tabla("B")
    assert ajustar(T, C, 0)(400.0) == pytest.approx(promedio_tabla("B"))
    assert promedio_tabla("B") == pytest.approx(3730 / 7)


# Las ecuaciones normales implementadas deben dar el mismo polinomio que una librería
# de referencia (numpy.polyfit, que usa otro algoritmo) para todos los grados.
@pytest.mark.parametrize("grado", range(7))
def test_coincide_con_polyfit_de_numpy(grado):
    T, C = tabla("B")
    propio = ajustar(T, C, grado)
    referencia = np.polyval(np.polyfit(T, C, grado), np.linspace(0, 800, 50))
    np.testing.assert_allclose(propio(np.linspace(0, 800, 50)), referencia, rtol=1e-8)


# Los coeficientes en T (los que se escriben en el informe) deben reproducir el polinomio evaluado.
def test_coeficientes_reproducen_el_ajuste():
    T, C = tabla("B")
    ajuste = ajustar(T, C, 3)
    a = ajuste.coeficientes()
    assert sum(a[i] * 350.0**i for i in range(len(a))) == pytest.approx(ajuste(350.0))


# Agregar grados nunca puede empeorar un ajuste de mínimos cuadrados.
def test_residuo_no_aumenta_con_el_grado():
    sse = [a.suma_cuadrados_residuos for a in ajustes_hasta_interpolante(*tabla("D"))]
    assert all(b <= a + 1e-9 for a, b in zip(sse, sse[1:]))


# Un grado mayor al interpolante no tiene solución única: debe rechazarse.
def test_rechaza_grado_mayor_al_interpolante():
    with pytest.raises(ValueError, match="grado"):
        ajustar(*tabla("B"), grado=7)
