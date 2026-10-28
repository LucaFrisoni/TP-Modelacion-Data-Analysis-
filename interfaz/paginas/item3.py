"""Ítem 3: calibración manual de T1 y T2 para Sk = 10 min manteniendo el Tsk del Ítem 2c."""

import streamlit as st

from calculos.datos import enunciado as E
from calculos.items import item3
from interfaz.componentes import calibracion_manual
from interfaz.componentes.comun import configuracion, planteo

cfg = configuracion()
op = cfg.operacion_base()
tsk_obj = item3.tsk_objetivo(cfg)
st.title("Ítem 3 · Calibración manual")
planteo(
    "Planteo del Ítem 3",
    f"Modelo completo: **radiación + C(T)** (grado {cfg.grado_c}), cadencia **{op.cad_s:g} s**. "
    f"Hay que encontrar T1 y T2 tales que **Sk = {E.SK_OBJETIVO_MIN:g} ± {E.TOL_SK_MIN:g} min** y "
    f"**Tsk = {tsk_obj:.4g} ± {E.TOL_TSK_C:g} °C** (el Tsk del Ítem 2c).\n\n"
    f"Se parte de las temperaturas del Ítem 1 (T1 = T2 = {op.T1_C:g} °C). Cada combinación probada es "
    f"una iteración. T1 actúa sobre la primera mitad del recorrido y T2 sobre la segunda.\n\n"
    f"Sk solo puede variar de a una cadencia (**{op.cad_s / 60:.3g} min**): cambios chicos de temperatura "
    "pueden no modificarlo.")
calibracion_manual.panel("3", cfg, op, tsk_obj, (op.T1_C, op.T2_C))
