"""Ítem 6: tabla resumen con 3 cifras significativas, armada con los resultados de cada ítem."""

import streamlit as st

from calculos.items import item5, item6
from interfaz.componentes import resultados_sesion
from interfaz.componentes.comun import configuracion, descarga_csv
from interfaz.componentes.descargas import CLAVE_METODO

cfg = configuracion()
st.title("Ítem 6 · Síntesis de resultados")
st.markdown(
    "Resultados con **3 cifras significativas**. La columna *Origen* indica de dónde sale cada valor:\n"
    "- **Ítems 1 y 2b:** calculados por el modelo.\n"
    "- **Ítems 3 y 4:** la calibración marcada con *Usar como resultado* en esta sesión o, si no hay, la "
    "definida por el equipo.\n"
    "- **Ítem 5:** el método elegido abajo con la configuración activa del Ítem 5.")
nombre_config, opciones = resultados_sesion.opciones_activas()
metodo = st.selectbox("Método del Ítem 5", item5.METODOS,
                      index=item5.METODOS.index(st.session_state.get(CLAVE_METODO, item5.METODOS[0])))
st.session_state[CLAVE_METODO] = metodo  # lo usan las descargas del panel lateral
with st.spinner("Calculando…"):
    df = item6.tabla_resumen(cfg, resultados_sesion.calibracion("3"), resultados_sesion.calibracion("4"),
                             opciones, metodo)
st.table(df.set_index("Ítem"))
st.caption(f"Ítem 5 calculado con la configuración «{nombre_config}».")
descarga_csv(df, "item6_resumen.csv")
