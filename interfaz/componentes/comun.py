"""Componentes compartidos: configuración vigente, gráficos, descargas y recuadros."""

import pandas as pd
import streamlit as st

from calculos.items.configuracion import Configuracion
from calculos.presentacion.graficos import CONFIG, version_oscura
from interfaz.componentes.apariencia import modo_oscuro

CLAVE_CFG = "configuracion"


def configuracion() -> Configuracion:
    return st.session_state.get(CLAVE_CFG) or Configuracion()


def grafico(fig, clave: str | None = None):
    """Gráfico Plotly con los colores del tema activo; el ícono de cámara lo descarga en PNG."""
    fig = version_oscura(fig) if modo_oscuro() else fig
    st.plotly_chart(fig, width="stretch", config=CONFIG, theme=None, key=clave)


def descarga_csv(df: pd.DataFrame, nombre: str, etiqueta: str = "Descargar CSV", clave: str | None = None):
    st.download_button(etiqueta, df.to_csv(index=False).encode("utf-8-sig"), file_name=nombre,
                       mime="text/csv", icon=":material/download:", key=clave)


def planteo(titulo: str, texto: str, ecuaciones: tuple[str, ...] = ()):
    """Recuadro con lo que cambia en el ítem respecto del planteo general."""
    with st.container(border=True):
        st.markdown(f"**{titulo}**")
        st.markdown(texto)
        for ecuacion in ecuaciones:
            st.latex(ecuacion)


def estado(ok: bool, texto: str):
    """Indicador de cumplimiento con ícono y texto (no solo color)."""
    (st.success if ok else st.error)(texto, icon=":material/check_circle:" if ok else ":material/cancel:")
