"""Parámetros derivados del problema: masa, superficie, velocidad y condición de operación."""

import math
from dataclasses import dataclass, replace

from calculos.datos import enunciado as E


@dataclass(frozen=True)
class Operacion:
    """Condición de operación del horno: cadencia [s] y temperaturas de zona [°C]."""

    cad_s: float
    T1_C: float
    T2_C: float

    def __post_init__(self):
        if self.cad_s <= 0:
            raise ValueError(f"La cadencia debe ser positiva (se recibió {self.cad_s})")

    def con_temperaturas(self, T1_C: float, T2_C: float) -> "Operacion":
        return replace(self, T1_C=T1_C, T2_C=T2_C)

    def con_cadencia(self, cad_s: float) -> "Operacion":
        return replace(self, cad_s=cad_s)


def operacion_base(nref: float) -> Operacion:
    """Operación del Ítem 1: cadencia y T1 = T2 calculadas a partir de NREF."""
    T = E.temperatura_zona_c(nref)
    return Operacion(cad_s=E.cadencia_s(nref), T1_C=T, T2_C=T)


def masa_kg() -> float:
    """m = rho * pi * OD * WT * (1 - WT/OD) * Lt (fórmula del enunciado)."""
    return E.RHO * math.pi * E.OD * E.WT * (1.0 - E.WT / E.OD) * E.LT


def superficie_m2() -> float:
    """S = pi * OD * Lt (superficie lateral exterior)."""
    return math.pi * E.OD * E.LT


def velocidad_m_s(cad_s: float) -> float:
    """v0 = L / (n° bolsillos * cad)."""
    return E.L_HORNO / (E.N_BOLSILLOS * cad_s)


def tiempo_en_horno_s(cad_s: float) -> float:
    """Tiempo que tarda el tubo en recorrer el horno: L / v0 = n° bolsillos * cad."""
    return E.N_BOLSILLOS * cad_s


def constante_tiempo_conveccion_s(c: float) -> float:
    """tau = m C / (hc S): escala de tiempo del modelo con solo convección."""
    return masa_kg() * c / (E.HC * superficie_m2())


def cadencia_por_productividad(cad_s: float, incremento: float) -> float:
    """Cadencia que aumenta la productividad en `incremento` (0.15 = +15 %).

    TODO: VALIDAR FÓRMULA O CRITERIO — supone productividad proporcional a 1/cad
    (tubos por hora con la misma cantidad de bolsillos). Debe justificarlo el equipo.
    """
    if incremento <= -1.0:
        raise ValueError("El incremento de productividad debe ser mayor que -100 %")
    return cad_s / (1.0 + incremento)
