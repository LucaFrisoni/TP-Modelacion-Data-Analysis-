"""Calibración manual (Ítems 3 y 4): probar T1 y T2, ver el resultado y numerar las iteraciones."""

import pandas as pd
import streamlit as st

from calculos.datos import enunciado as E
from calculos.items import item3
from calculos.modelo.parametros import Operacion
from calculos.presentacion import graficos as G
from interfaz.componentes import resultados_sesion
from interfaz.componentes.comun import descarga_csv, estado, grafico


def _entradas(clave: str, inicial: tuple[float, float]) -> tuple[float, float]:
    c1, c2 = st.columns(2)
    T1 = c1.number_input("T1 – zona 1 [°C]", value=float(inicial[0]), step=1.0, key=f"{clave}_T1")
    T2 = c2.number_input("T2 – zona 2 [°C]", value=float(inicial[1]), step=1.0, key=f"{clave}_T2")
    return T1, T2


def _indicadores(sk, tsk_obj: float) -> item3.Verificacion:
    v = item3.verificar_objetivo(sk, tsk_obj)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Sk", f"{sk.sk_min:.3g} min", f"{sk.sk_min - E.SK_OBJETIVO_MIN:+.2f} min vs objetivo",
                  delta_color="off")
        estado(v.sk_ok, f"Sk dentro de {E.SK_OBJETIVO_MIN:g} ± {E.TOL_SK_MIN:g} min" if v.sk_ok
               else "Sk fuera de tolerancia")
    with c2:
        st.metric("Tsk", f"{sk.tsk_C:.4g} °C", f"{sk.tsk_C - tsk_obj:+.2f} °C vs objetivo", delta_color="off")
        estado(v.tsk_ok, f"Tsk dentro de {tsk_obj:.4g} ± {E.TOL_TSK_C:g} °C" if v.tsk_ok
               else "Tsk fuera de tolerancia")
    return v


def _historial(clave: str, op: Operacion, sk, v):
    historial = st.session_state.setdefault(f"{clave}_historial", [])
    item3.registrar_iteracion(historial, op, sk, v)
    st.subheader("Iteraciones")
    st.caption("Cada combinación de T1 y T2 que se prueba queda registrada con su número de iteración.")
    df = pd.DataFrame(historial)
    st.dataframe(df, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        descarga_csv(df, f"iteraciones_item{clave[-1]}.csv", "Descargar iteraciones", clave=f"{clave}_dl")
    if c2.button("Reiniciar iteraciones", key=f"{clave}_reiniciar", icon=":material/restart_alt:"):
        historial.clear()
        st.rerun()


def _usar_como_resultado(item: str, op: Operacion, v: item3.Verificacion):
    if st.button(f"Usar como resultado del Ítem {item}", key=f"usar_item{item}", type="primary",
                 icon=":material/done_all:"):
        resultados_sesion.guardar_calibracion(item, op.T1_C, op.T2_C)
        st.toast(f"T1 = {op.T1_C:g} °C y T2 = {op.T2_C:g} °C guardadas como resultado del Ítem {item}.")
    if not v.cumple:
        st.caption("Ojo: la combinación actual todavía no cumple las dos tolerancias.")


def panel(item: str, cfg, op: Operacion, tsk_obj: float, inicial: tuple[float, float]):
    """Simula con el modelo completo (radiación + C(T)) y muestra resultados e iteraciones."""
    clave = f"item{item}"
    op = op.con_temperaturas(*_entradas(clave, inicial))
    res, sk = item3.evaluar_operacion(cfg, op)
    v = _indicadores(sk, tsk_obj)
    _usar_como_resultado(item, op, v)
    grafico(G.soaking(res, sk, op, f"Evolución térmica – cad = {op.cad_s:.4g} s"), clave=f"{clave}_fig")
    _historial(clave, op, sk, v)
    return op, res, sk
