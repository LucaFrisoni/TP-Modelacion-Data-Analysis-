"""Panel lateral: tema, datos del grupo, decisiones del equipo y descargas de todos los resultados."""

import streamlit as st

from calculos.datos import decisiones as D
from calculos.datos import enunciado as E
from calculos.datos import grupo
from calculos.items.configuracion import Configuracion
from calculos.modelo.soaking import CONVENCIONES_SK
from interfaz.componentes import apariencia, descargas
from interfaz.componentes.comun import CLAVE_CFG

_AYUDA_SK = ("intervalos: suma de los intervalos con ambos extremos dentro de la banda.\n\n"
             "puntos: cantidad de puntos dentro de la banda × h.")


def _decisiones() -> Configuracion:
    """Las dos decisiones que afectan a varios ítems."""
    st.header("Decisiones del equipo")
    grado = st.selectbox("Grado del polinomio C(T)", range(len(E.TEMPERATURAS_TABLA_C)), index=D.GRADO_C,
                         help="Se usa en los Ítems 2a, 3, 4 y 5.")
    conv = st.radio("Conteo del tiempo de soaking", CONVENCIONES_SK,
                    index=CONVENCIONES_SK.index(D.CONVENCION_SK), help=_AYUDA_SK)
    return Configuracion(grado_c=grado, convencion_sk=conv)


def panel_lateral():
    apariencia.estilos()
    with st.sidebar:
        apariencia.interruptor_tema()
        st.header("Datos del grupo")
        st.markdown(f"**NREF** = {grupo.NREF}  \n**Tabla de calor específico:** {grupo.TABLA_C}")
        st.session_state[CLAVE_CFG] = _decisiones()
        st.header("Descargas")
        descargas.botones()
