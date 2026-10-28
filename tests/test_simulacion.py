"""Pruebas de la simulación completa, la solución analítica y el error relativo."""

import numpy as np
import pytest

from calculos.datos import enunciado as E
from calculos.modelo.calor_especifico import calor_constante
from calculos.modelo.modelo_termico import ModeloTermico
from calculos.modelo.parametros import Operacion
from calculos.modelo.simulacion import Resultado, error_relativo, simular, solucion_analitica

OP = Operacion(cad_s=30.0, T1_C=625.0, T2_C=625.0)
C = 541.43


# Validación central del Ítem 1: RK2 con h = cad debe reproducir la solución exacta
# (h/τ ≈ 0.01, el error relativo esperable es del orden de 1e-5).
def test_rk2_reproduce_solucion_analitica_en_el_item_1():
    res = simular(ModeloTermico(OP, calor_constante(C)), "rk2")
    exacta = solucion_analitica(OP, C, res.t_s)
    assert np.max(error_relativo(res, exacta)) < 1e-4


# La simulación debe cubrir exactamente el recorrido del horno: 50 pasos de una cadencia
# y arrancar en la condición inicial de 20 °C.
def test_simulacion_recorre_el_horno_completo_desde_20_grados():
    res = simular(ModeloTermico(OP, calor_constante(C)), "euler")
    assert len(res.t_s) == E.N_BOLSILLOS + 1
    assert res.t_min[-1] == pytest.approx(E.N_BOLSILLOS * 30.0 / 60)
    assert res.T_C[0] == pytest.approx(E.T0_C)


# Comportamiento físico esperado con radiación: calentamiento monótono sin superar
# la temperatura del horno (superarla indicaría inestabilidad o un signo mal puesto).
def test_con_radiacion_calienta_monotonamente_sin_superar_el_horno():
    res = simular(ModeloTermico(OP, calor_constante(C), radiacion=True), "rk2")
    assert np.all(np.diff(res.T_C) > 0)
    assert res.T_C.max() < OP.T1_C


# Subdividir el paso debe mantener los mismos instantes de inicio y fin.
def test_subpasos_refinan_sin_cambiar_el_intervalo():
    res = simular(ModeloTermico(OP, calor_constante(C)), "rk2", subpasos=4)
    assert len(res.t_s) == 4 * E.N_BOLSILLOS + 1
    assert res.t_s[-1] == pytest.approx(E.N_BOLSILLOS * 30.0)


# La solución analítica solo vale con T1 = T2; usarla en otro caso sería un error conceptual.
def test_solucion_analitica_rechaza_zonas_distintas():
    with pytest.raises(ValueError, match="T1 = T2"):
        solucion_analitica(Operacion(30.0, 700.0, 600.0), C, [0.0, 30.0])


# El error relativo depende de la escala (pendiente del equipo): en °C el denominador
# es menor y el error resulta mayor que en K para la misma diferencia absoluta.
def test_error_relativo_en_celsius_es_mayor_que_en_kelvin():
    t = np.array([0.0, 30.0])
    num, exa = Resultado(t, np.array([400.0, 500.0])), Resultado(t, np.array([400.0, 499.0]))
    assert error_relativo(num, exa, "C")[1] > error_relativo(num, exa, "K")[1]
    assert error_relativo(num, exa, "K")[1] == pytest.approx(1 / 499.0)
