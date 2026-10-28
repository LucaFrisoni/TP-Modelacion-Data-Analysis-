"""Conversión de unidades: los cálculos van en K y s, los resultados en °C y min."""

from calculos.datos.enunciado import KELVIN_OFFSET


def c_a_k(T_C):
    return T_C + KELVIN_OFFSET


def k_a_c(T_K):
    return T_K - KELVIN_OFFSET


def s_a_min(t_s):
    return t_s / 60.0
