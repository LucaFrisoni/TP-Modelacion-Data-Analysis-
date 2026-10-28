"""Opciones de los métodos del Ítem 5: edición, configuraciones con nombre, exportar e importar JSON.

Las configuraciones viven en la sesión del navegador; para conservarlas entre sesiones se
descargan en JSON y se vuelven a importar.
"""

import json

import streamlit as st

from calculos.items.item5 import OpcionesMetodo
from interfaz.componentes import resultados_sesion
from interfaz.componentes.resultados_sesion import NOMBRE_PREDETERMINADA

_CONFIGS = "i5_configs"


def _a_widgets(op: OpcionesMetodo) -> dict:
    (j11, j12), (j21, j22) = op.J_punto_fijo
    return {"i5_delta": op.delta_C, "i5_d1": op.desplazamiento_inicial_C[0],
            "i5_d2": op.desplazamiento_inicial_C[1], "i5_tol1": op.tolerancias[0],
            "i5_tol2": op.tolerancias[1], "i5_maxit": op.max_iteraciones, "i5_sub": op.subpasos,
            "i5_amort": op.amortiguado, "i5_J11": j11, "i5_J12": j12, "i5_J21": j21, "i5_J22": j22}


def _desde_widgets() -> OpcionesMetodo:
    s = st.session_state
    return OpcionesMetodo(
        delta_C=s.i5_delta, desplazamiento_inicial_C=(s.i5_d1, s.i5_d2), tolerancias=(s.i5_tol1, s.i5_tol2),
        max_iteraciones=int(s.i5_maxit), subpasos=int(s.i5_sub), amortiguado=s.i5_amort,
        J_punto_fijo=((s.i5_J11, s.i5_J12), (s.i5_J21, s.i5_J22)))


def _inicializar():
    """Crea las configuraciones y repone los valores de los controles al volver a la página."""
    s = st.session_state
    s.setdefault(_CONFIGS, {NOMBRE_PREDETERMINADA: OpcionesMetodo().a_dict()})
    nombre, activas = resultados_sesion.opciones_activas()
    if "i5_delta" not in s:
        s.update(_a_widgets(activas))
    if "i5_sel" not in s:
        s.i5_sel = nombre.removesuffix(" (modificada)")


def _cargar_seleccion():
    s = st.session_state
    s.update(_a_widgets(OpcionesMetodo.desde_dict(s[_CONFIGS][s.i5_sel])))


def _guardar():
    s = st.session_state
    nombre = s.i5_nombre.strip()
    if not nombre:
        s.i5_aviso = "Escribí un nombre para la configuración."
        return
    s[_CONFIGS][nombre] = _desde_widgets().a_dict()
    s.i5_sel, s.i5_aviso = nombre, f"Configuración «{nombre}» guardada."


def _controles_iteracion():
    c1, c2, c3 = st.columns(3)
    c1.number_input("Δ para diferencias finitas [°C]", min_value=0.01, key="i5_delta")
    c2.number_input("T1 inicial = Tsk objetivo + … [°C]", key="i5_d1")
    c3.number_input("T2 inicial = Tsk objetivo + … [°C]", key="i5_d2")
    c1, c2, c3 = st.columns(3)
    c1.number_input("Tolerancia |F1| [°C]", min_value=1e-6, format="%.3f", key="i5_tol1")
    c2.number_input("Tolerancia |F2| [min]", min_value=1e-6, format="%.3f", key="i5_tol2")
    c3.number_input("Máximo de iteraciones", min_value=1, step=1, key="i5_maxit")


def _controles_avanzados():
    c1, c2 = st.columns(2)
    c1.number_input("Subpasos por cadencia (h = cad / n)", min_value=1, max_value=20, step=1, key="i5_sub",
                    help="1 = paso del enunciado. Valores mayores suavizan los escalones de Sk.")
    c2.checkbox("Amortiguar el paso", key="i5_amort",
                help="Reduce el paso a la mitad mientras el residuo no mejore.")
    st.markdown("J constante para punto fijo (la identidad es la del enunciado):")
    for col, clave in zip(st.columns(4), ("i5_J11", "i5_J12", "i5_J21", "i5_J22")):
        col.number_input(clave.removeprefix("i5_"), key=clave)


def _importar(archivo):
    s = st.session_state
    if archivo is None or s.get("i5_importado") == archivo.file_id:
        return
    try:
        nuevas = {n: OpcionesMetodo.desde_dict(d).a_dict() for n, d in json.load(archivo).items()}
    except (ValueError, TypeError, AttributeError) as error:
        st.error(f"El archivo no es una configuración válida: {error}")
        return
    s[_CONFIGS].update(nuevas)
    s.i5_importado = archivo.file_id
    st.success(f"Se importaron {len(nuevas)} configuraciones.")


def _guardar_y_exportar():
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    c1.text_input("Nombre para guardar la configuración actual", key="i5_nombre",
                  placeholder="Ej.: Newton con Δ = 5 °C")
    c2.button("Guardar", on_click=_guardar, icon=":material/save:")
    if aviso := st.session_state.pop("i5_aviso", None):
        st.caption(aviso)
    datos = json.dumps(st.session_state[_CONFIGS], ensure_ascii=False, indent=2)
    st.download_button("Descargar configuraciones (JSON)", datos, "configuraciones_item5.json",
                       mime="application/json", icon=":material/download:")
    _importar(st.file_uploader("Importar configuraciones (JSON)", type="json", key="i5_archivo"))


def seleccionar() -> tuple[str, OpcionesMetodo]:
    """Muestra el selector y los controles; devuelve (nombre, opciones) en uso y los deja activos."""
    _inicializar()
    configs = st.session_state[_CONFIGS]
    st.selectbox("Configuración", list(configs), key="i5_sel", on_change=_cargar_seleccion)
    with st.expander("Opciones del método"):
        _controles_iteracion()
        _controles_avanzados()
    with st.expander("Guardar, descargar o importar configuraciones"):
        _guardar_y_exportar()
    opciones, nombre = _desde_widgets(), st.session_state.i5_sel
    if opciones.a_dict() != configs[nombre]:
        nombre += " (modificada)"
    resultados_sesion.guardar_opciones_activas(nombre, opciones)
    return nombre, opciones
