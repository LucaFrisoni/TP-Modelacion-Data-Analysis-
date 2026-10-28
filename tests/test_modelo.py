"""Pruebas del modelo térmico: zonas del horno, unidades de C(T), equilibrio y radiación."""

import pytest

from calculos.datos import enunciado as E
from calculos.modelo.calor_especifico import calor_constante
from calculos.modelo.modelo_termico import ModeloTermico
from calculos.modelo.parametros import Operacion, tiempo_en_horno_s
from calculos.modelo.unidades import c_a_k

OP = Operacion(cad_s=30.0, T1_C=700.0, T2_C=600.0)


# El punto x = L/2 pertenece a la zona 1 (T∞ = T1 si x <= L/2). Con h = cad cae
# exactamente en un nodo, y un redondeo no debe cambiarlo de zona.
def test_mitad_del_horno_pertenece_a_zona_1_y_luego_cambia_a_zona_2():
    m = ModeloTermico(OP, calor_constante(540.0))
    t_mitad = 25 * OP.cad_s
    assert m.temperatura_entorno_K(t_mitad) == pytest.approx(c_a_k(700.0))
    assert m.temperatura_entorno_K(t_mitad + 1e-3) == pytest.approx(c_a_k(600.0))
    assert m.temperatura_entorno_K(tiempo_en_horno_s(OP.cad_s)) == pytest.approx(c_a_k(600.0))


# Regresión de unidades: la tabla de C está en °C pero el modelo trabaja en K.
# C(T) debe recibir la temperatura en °C.
def test_calor_especifico_recibe_temperatura_en_celsius():
    recibidas = []
    m = ModeloTermico(OP, lambda T_C: recibidas.append(T_C) or 540.0)
    m.derivada(0.0, c_a_k(200.0))
    assert recibidas == [pytest.approx(200.0)]


# Si el tubo ya está a la temperatura del horno, no hay intercambio de calor.
@pytest.mark.parametrize("radiacion", [False, True])
def test_equilibrio_termico_no_cambia_la_temperatura(radiacion):
    m = ModeloTermico(OP, calor_constante(540.0), radiacion)
    assert m.derivada(0.0, c_a_k(700.0)) == pytest.approx(0.0, abs=1e-12)


# La radiación agrega calor cuando el horno está más caliente: el calentamiento debe ser mayor.
def test_radiacion_acelera_el_calentamiento():
    sin = ModeloTermico(OP, calor_constante(540.0), radiacion=False)
    con = ModeloTermico(OP, calor_constante(540.0), radiacion=True)
    T = c_a_k(400.0)
    assert con.derivada(0.0, T) > sin.derivada(0.0, T) > 0


# Un ajuste C(T) que se vuelva negativo daría temperaturas sin sentido físico:
# debe detenerse con un mensaje en lugar de seguir calculando.
def test_calor_especifico_no_positivo_lanza_error():
    m = ModeloTermico(OP, lambda T_C: -1.0)
    with pytest.raises(ValueError, match="C\\(T\\) no positivo"):
        m.derivada(0.0, c_a_k(300.0))
