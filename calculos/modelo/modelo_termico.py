"""Modelo térmico de parámetros concentrados del tubo dentro del horno.

    -m C(T) dT/dt = hc S (T - T∞) + σ ε S (T^4 - T∞^4)

Las temperaturas internas están en K y el tiempo en s. C(T) recibe °C porque
las tablas del enunciado están en °C.
"""

from dataclasses import dataclass

from calculos.datos import enunciado as E
from calculos.modelo.calor_especifico import FuncionCalor
from calculos.modelo.parametros import Operacion, masa_kg, superficie_m2, velocidad_m_s
from calculos.modelo.unidades import c_a_k, k_a_c

# Tolerancia relativa para decidir si x = v0 t cae exactamente en L/2: evita que
# un error de redondeo cambie de zona el punto de la mitad del horno.
_TOL_MITAD_HORNO = 1e-9


@dataclass(frozen=True)
class ModeloTermico:
    """Ecuación diferencial del tubo para una operación y un C(T) dados."""

    operacion: Operacion
    calor_especifico: FuncionCalor
    radiacion: bool = False

    def temperatura_entorno_K(self, t_s: float) -> float:
        """T∞(x) por tramos: T1 si x <= L/2, T2 si x > L/2, con x = v0 t."""
        x = velocidad_m_s(self.operacion.cad_s) * t_s
        mitad = E.L_HORNO / 2
        en_zona_1 = x <= mitad * (1 + _TOL_MITAD_HORNO)
        return c_a_k(self.operacion.T1_C if en_zona_1 else self.operacion.T2_C)

    def flujo_calor_W(self, t_s: float, T_K: float) -> float:
        """Potencia que entra al tubo por convección (+ radiación si está activa)."""
        T_inf = self.temperatura_entorno_K(t_s)
        S = superficie_m2()
        q = E.HC * S * (T_inf - T_K)
        if self.radiacion:
            q += E.SIGMA * E.EPSILON * S * (T_inf**4 - T_K**4)
        return q

    def derivada(self, t_s: float, T_K: float) -> float:
        """dT/dt [K/s] = flujo / (m C(T))."""
        c = self.calor_especifico(k_a_c(T_K))
        if c <= 0:
            raise ValueError(f"C(T) no positivo ({c:.3g}) a T = {k_a_c(T_K):.1f} °C")
        return self.flujo_calor_W(t_s, T_K) / (masa_kg() * c)
