"""Simulación del tubo a lo largo del horno, solución analítica y error relativo."""

from dataclasses import dataclass
import numpy as np
from calculos.datos import enunciado as E
from calculos.metodos.integradores import METODOS
from calculos.modelo.modelo_termico import ModeloTermico
from calculos.modelo.parametros import Operacion, masa_kg, superficie_m2, tiempo_en_horno_s
from calculos.modelo.unidades import c_a_k, k_a_c, s_a_min


@dataclass(frozen=True)
class Resultado:
    """Evolución térmica calculada: tiempo [s] y temperatura [K]."""

    t_s: np.ndarray
    T_K: np.ndarray

    @property
    def t_min(self) -> np.ndarray:
        return s_a_min(self.t_s)

    @property
    def T_C(self) -> np.ndarray:
        return k_a_c(self.T_K)

    @property
    def T_final_C(self) -> float:
        return float(self.T_C[-1])


def simular(modelo: ModeloTermico, metodo: str = "rk2", subpasos: int = 1) -> Resultado:
    """Integra desde la entrada hasta la salida del horno (t = n° bolsillos * cad).

    El paso es h = cad / subpasos; subpasos = 1 es el paso pedido por el enunciado.
    """
    if metodo not in METODOS:
        raise ValueError(f"Método {metodo!r} desconocido. Opciones: {sorted(METODOS)}")
    if subpasos < 1:
        raise ValueError("subpasos debe ser un entero >= 1")
    h = modelo.operacion.cad_s / subpasos
    n_pasos = E.N_BOLSILLOS * subpasos
    t, T = METODOS[metodo](modelo.derivada, c_a_k(E.T0_C), 0.0, h, n_pasos)
    return Resultado(t, T)


def solucion_analitica(operacion: Operacion, c: float, t_s) -> Resultado:
    """T(t) = T∞ + (T0 - T∞) exp(-hc S t / (m C)). Válida solo con T1 = T2,
    sin radiación y con C constante (Ítem 1)."""
    if operacion.T1_C != operacion.T2_C:
        raise ValueError("La solución analítica requiere T1 = T2")
    t_s = np.asarray(t_s, float)
    T_inf, T0 = c_a_k(operacion.T1_C), c_a_k(E.T0_C)
    k = E.HC * superficie_m2() / (masa_kg() * c)
    return Resultado(t_s, T_inf + (T0 - T_inf) * np.exp(-k * t_s))


def malla_analitica(operacion: Operacion, c: float, n_puntos: int = 400) -> Resultado:
    """Solución analítica en una malla fina, para graficarla como curva continua."""
    t = np.linspace(0.0, tiempo_en_horno_s(operacion.cad_s), n_puntos)
    return solucion_analitica(operacion, c, t)


def error_relativo(
    numerico: Resultado, exacto: Resultado, escala: str = "K"
) -> np.ndarray:
    """|T_num - T_exacta| / |T_exacta| punto a punto, en la escala elegida ("K" o "C").

    TODO: VALIDAR FÓRMULA O CRITERIO — la escala la define el equipo
    (ver ESCALA_ERROR_RELATIVO en calculos/datos/decisiones.py).
    """
    if not np.allclose(numerico.t_s, exacto.t_s):
        raise ValueError("Las soluciones deben estar evaluadas en los mismos tiempos")
    if escala not in ("K", "C"):
        raise ValueError("La escala debe ser 'K' o 'C'")
    a, b = (numerico.T_K, exacto.T_K) if escala == "K" else (numerico.T_C, exacto.T_C)
    return np.abs(a - b) / np.abs(b)
