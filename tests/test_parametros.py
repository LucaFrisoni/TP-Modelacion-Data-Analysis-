"""Pruebas de los parámetros derivados del enunciado (cadencia, masa, superficie, velocidad)."""

import math

import pytest

from calculos.datos import enunciado as E
from calculos.modelo import parametros as P


# El enunciado da un ejemplo explícito (NREF = 0.5 -> cad = 30 s, T1 = T2 = 625 °C):
# es el único oráculo externo disponible para las fórmulas con NREF.
def test_operacion_base_reproduce_ejemplo_del_enunciado():
    op = P.operacion_base(0.5)
    assert (op.cad_s, op.T1_C, op.T2_C) == (30.0, 625.0, 625.0)


# La fórmula de masa del enunciado debe coincidir con densidad × volumen de una corona
# circular calculado de forma independiente: un error de transcripción cambiaría todo el TP.
def test_masa_coincide_con_volumen_de_corona_circular():
    diametro_interior = E.OD - 2 * E.WT
    volumen = math.pi / 4 * (E.OD**2 - diametro_interior**2) * E.LT
    assert P.masa_kg() == pytest.approx(E.RHO * volumen, rel=1e-12)


# El tubo debe recorrer el horno en n° bolsillos × cad; si v0 estuviera mal, la
# simulación terminaría en un instante incorrecto.
def test_velocidad_recorre_el_horno_en_n_bolsillos_por_cadencia():
    cad = 27.5
    assert E.L_HORNO / P.velocidad_m_s(cad) == pytest.approx(P.tiempo_en_horno_s(cad))
    assert P.tiempo_en_horno_s(cad) == pytest.approx(E.N_BOLSILLOS * cad)


# +15 % de productividad con 1/cad: la nueva cadencia produce 1.15 veces más tubos por hora.
def test_cadencia_por_productividad_aumenta_tubos_por_hora_15_por_ciento():
    cad_nueva = P.cadencia_por_productividad(30.0, 0.15)
    assert (1 / cad_nueva) / (1 / 30.0) == pytest.approx(1.15)


# Entradas imposibles deben fallar con un mensaje claro y no producir resultados absurdos.
def test_operacion_rechaza_cadencia_no_positiva():
    with pytest.raises(ValueError, match="cadencia"):
        P.Operacion(cad_s=0.0, T1_C=600.0, T2_C=600.0)
