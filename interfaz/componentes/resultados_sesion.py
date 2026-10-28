"""Resultados que pasan de un ítem a otro (calibraciones y configuración del Ítem 5).

Lo elegido en la sesión tiene prioridad; si no hay, se usa lo definido en decisiones.py.
La sesión se pierde al recargar la página.
"""

import streamlit as st

from calculos.datos import decisiones as D
from calculos.items.item5 import OpcionesMetodo
from calculos.items.item6 import Calibracion

_DEFINIDAS = {"3": D.CALIBRACION_ITEM3_C, "4": D.CALIBRACION_ITEM4_C}
NOMBRE_PREDETERMINADA = "Predeterminada"


def guardar_calibracion(item: str, T1_C: float, T2_C: float):
    st.session_state[f"resultado_item{item}"] = (T1_C, T2_C)


def calibracion(item: str) -> Calibracion | None:
    """Calibración vigente del ítem 3 o 4, con su origen."""
    en_sesion = st.session_state.get(f"resultado_item{item}")
    if en_sesion:
        return Calibracion(*en_sesion, origen="Elegida en esta sesión")
    if _DEFINIDAS[item]:
        return Calibracion(*_DEFINIDAS[item], origen="Definida por el equipo")
    return None


def guardar_opciones_activas(nombre: str, opciones: OpcionesMetodo):
    st.session_state["item5_activa"] = (nombre, opciones)


def opciones_activas() -> tuple[str, OpcionesMetodo]:
    """Configuración del Ítem 5 en uso (la predeterminada si todavía no se eligió otra)."""
    return st.session_state.get("item5_activa", (NOMBRE_PREDETERMINADA, OpcionesMetodo()))
