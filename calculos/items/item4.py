"""Ítem 4: cadencia para aumentar la productividad un 15 % manteniendo Sk y Tsk."""

from calculos.datos import enunciado as E
from calculos.items.configuracion import Configuracion
from calculos.modelo.parametros import Operacion, cadencia_por_productividad


def cadencia_nueva_s(cfg: Configuracion) -> float:
    return cadencia_por_productividad(cfg.operacion_base().cad_s, E.INCREMENTO_PRODUCTIVIDAD)


def operacion_nueva(cfg: Configuracion, T1_C: float, T2_C: float) -> Operacion:
    """Operación con la cadencia reducida y las temperaturas que se estén probando."""
    return cfg.operacion_base().con_cadencia(cadencia_nueva_s(cfg)).con_temperaturas(T1_C, T2_C)
