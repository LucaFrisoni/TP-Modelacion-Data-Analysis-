"""Aplicación web del TP: navegación entre la introducción y los 6 ítems, y panel lateral.

Ejecutar con:  docker compose up   (o  streamlit run app.py)
"""

import streamlit as st

from interfaz.componentes.apariencia import RECURSOS, esqueleto
from interfaz.componentes.panel_lateral import panel_lateral

st.set_page_config(page_title="TP Revenido – Modelación Numérica · FIUBA",
                   page_icon=str(RECURSOS / "emblema_fiuba_claro.png"), layout="wide")

PAGINAS = [
    st.Page("interfaz/paginas/introduccion.py", title="Introducción y parámetros", icon=":material/home:",
            default=True),
    st.Page("interfaz/paginas/item1.py", title="Ítem 1 · Euler vs RK2", icon=":material/show_chart:"),
    st.Page("interfaz/paginas/item2.py", title="Ítem 2 · C(T), radiación, soaking", icon=":material/thermostat:"),
    st.Page("interfaz/paginas/item3.py", title="Ítem 3 · Calibración manual", icon=":material/tune:"),
    st.Page("interfaz/paginas/item4.py", title="Ítem 4 · Productividad", icon=":material/speed:"),
    st.Page("interfaz/paginas/item5.py", title="Ítem 5 · Sistema no lineal", icon=":material/functions:"),
    st.Page("interfaz/paginas/item6.py", title="Ítem 6 · Síntesis de resultados", icon=":material/table:"),
]

navegacion = st.navigation(PAGINAS)
panel_lateral()
with esqueleto(navegacion.url_path):
    navegacion.run()
