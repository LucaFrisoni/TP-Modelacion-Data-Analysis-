"""Ítem 1: Euler explícito, RK2 y solución analítica (solo convección, C promedio)."""

import streamlit as st

from calculos.datos import decisiones as D
from calculos.items import item1
from calculos.presentacion import graficos as G
from interfaz.componentes.comun import configuracion, descarga_csv, grafico, planteo
from interfaz.componentes.descargas import CLAVE_ESCALA


def seccion_planteo(cfg):
    op = cfg.operacion_base()
    planteo(
        "Planteo del Ítem 1",
        f"Se desprecia la radiación y se usa C constante = promedio de la tabla {cfg.tabla_c} "
        f"(**{cfg.c_medio():.4g} J/kg K**). Con T1 = T2 = T∞ = **{op.T1_C:g} °C** y paso h = cad = "
        f"**{op.cad_s:g} s**, la ecuación es lineal y tiene solución exacta:",
        (r"-m\,\bar C\,\frac{dT}{dt} = h_c S\,(T - T_\infty)"
         r"\quad\Longrightarrow\quad T(t) = T_\infty + (T_0 - T_\infty)\,e^{-\frac{h_c S}{m \bar C}t}",))


def seccion_1a(res):
    st.subheader("1a · Evolución temporal")
    curvas = [G.Curva("Analítica", res["analitica"].t_min, res["analitica"].T_C, "lines", G.SERIES[0]),
              G.Curva("Euler explícito", res["euler"].t_min, res["euler"].T_C, color=G.SERIES[1]),
              G.Curva("RK2", res["rk2"].t_min, res["rk2"].T_C, "markers", G.SERIES[2])]
    grafico(G.evolucion(curvas, "Temperatura del tubo – solo convección, h = cad"))
    cols = st.columns(3)
    for col, (nombre, clave) in zip(cols, [("Analítica", "analitica"), ("Euler", "euler"), ("RK2", "rk2")]):
        col.metric(f"T final {nombre}", f"{res[clave].T_final_C:.4f} °C")


def controles_1b() -> tuple[str, bool]:
    c1, c2 = st.columns(2)
    eje = c1.radio("Escala del eje vertical", ("Logarítmica", "Lineal"), horizontal=True)
    previa = st.session_state.get(CLAVE_ESCALA, D.ESCALA_ERROR_RELATIVO)
    temperaturas = c2.radio("Temperaturas para el error", ("Kelvin", "Celsius"), horizontal=True,
                            index=0 if previa == "K" else 1,
                            help="El error relativo |T_num − T_exacta| / |T_exacta| depende de la escala: "
                                 "en °C el denominador es menor y el error resulta mayor.")
    escala = "K" if temperaturas == "Kelvin" else "C"
    st.session_state[CLAVE_ESCALA] = escala  # la usan las descargas del panel lateral
    return escala, eje == "Logarítmica"


def seccion_1b(res):
    st.subheader("1b · Error relativo")
    escala, logaritmico = controles_1b()
    err = item1.errores(res, escala)
    grafico(G.error_relativo(res["euler"].t_min, {"Euler explícito": err["euler"], "RK2": err["rk2"]},
                             escala, logaritmico))
    with st.expander("Tabla de puntos (para verificar a mano o en Excel)"):
        df = item1.tabla_puntos(res, err)
        st.dataframe(df, hide_index=True)
        descarga_csv(df, f"item1_puntos_{escala}.csv")
    return escala


def seccion_1c(cfg, escala: str):
    st.subheader("1c · Influencia del paso temporal")
    st.caption("Mismo problema con h = cad, cad/2, cad/4 y cad/8. Al dividir h por 2, el cociente entre "
               "errores estima el orden del método (≈2 → orden 1; ≈4 → orden 2).")
    df = item1.estudio_paso(cfg, escala)
    st.dataframe(df, hide_index=True, column_config={c: st.column_config.NumberColumn(format="%.4e")
                                                     for c in df.columns if "error" in c})
    descarga_csv(df, "item1_estudio_paso.csv")


cfg = configuracion()
st.title("Ítem 1 · Modelo simplificado y validación analítica")
seccion_planteo(cfg)
res = item1.resolver(cfg)
seccion_1a(res)
escala = seccion_1b(res)
seccion_1c(cfg, escala)
