"""Ítem 2: ajuste de C(T) siempre visible y pestañas para 2a (C variable), 2b (radiación) y 2c (soaking)."""

import streamlit as st

from calculos.datos import enunciado as E
from calculos.items import item2
from calculos.modelo.calor_especifico import tabla
from calculos.modelo.simulacion import malla_analitica
from calculos.presentacion import graficos as G
from interfaz.componentes.comun import configuracion, descarga_csv, grafico, planteo


def seccion_ajuste(cfg):
    st.subheader(f"Ajuste de C(T) por mínimos cuadrados – tabla {cfg.tabla_c}")
    ajustes = item2.ajustes(cfg)
    grafico(G.ajustes_calor(*tabla(cfg.tabla_c), ajustes, cfg.grado_c))
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Residuos de cada grado**")
        st.dataframe(item2.tabla_ajustes(ajustes), hide_index=True)
    with c2:
        st.markdown(f"**Polinomio elegido: grado {cfg.grado_c}** (T en °C; se cambia en el panel lateral)")
        st.dataframe(item2.tabla_coeficientes(cfg.ajuste_c()), hide_index=True,
                     column_config={"coeficiente": st.column_config.NumberColumn(format="%.6e")})


def comparar_con_exacta(cfg, res, nombre: str, titulo: str):
    exacta = malla_analitica(cfg.operacion_base(), cfg.c_medio())
    curvas = [G.Curva("Exacta del Ítem 1 (solo convección)", exacta.t_min, exacta.T_C, "lines", G.SERIES[0]),
              G.Curva(nombre, res.t_min, res.T_C, color=G.SERIES[1])]
    grafico(G.evolucion(curvas, titulo))
    c1, c2 = st.columns(2)
    c1.metric("T final exacta (Ítem 1)", f"{exacta.T_final_C:.2f} °C")
    c2.metric(f"T final {nombre}", f"{res.T_final_C:.2f} °C", f"{res.T_final_C - exacta.T_final_C:+.2f} °C")


def tab_2a(cfg):
    planteo("Qué cambia en el 2a",
            f"C depende de la temperatura: se usa el polinomio de grado {cfg.grado_c} ajustado arriba. "
            "Sin radiación, T1 = T2.",
            (r"-m\,C(T)\,\frac{dT}{dt} = h_c S\,(T - T_\infty)",))
    comparar_con_exacta(cfg, item2.item2a(cfg), "RK2 con C(T)", "Ítem 2a – calor específico variable")


def tab_2b(cfg):
    planteo("Qué cambia en el 2b",
            f"Se agrega la radiación y se vuelve a usar C promedio ({cfg.c_medio():.4g} J/kg K). T1 = T2.",
            (r"-m\,\bar C\,\frac{dT}{dt} = h_c S\,(T - T_\infty) + \sigma\varepsilon S\,(T^4 - T_\infty^4)",))
    comparar_con_exacta(cfg, item2.item2b(cfg), "RK2 con radiación", "Ítem 2b – convección + radiación")


def tab_2c(cfg):
    planteo("Qué se calcula en el 2c",
            f"Sobre los puntos del 2b: **Sk** = tiempo acumulado con T dentro de la banda "
            f"[T final − {E.ANCHO_BANDA_SOAKING_C:g} °C, T final]; **Tsk** = temperatura promedio en esa banda. "
            f"Conteo de Sk: *{cfg.convencion_sk}* (panel lateral).")
    res, sk = item2.item2c(cfg)
    grafico(G.soaking(res, sk, cfg.operacion_base(), "Ítem 2c – banda de soaking"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Sk", f"{sk.sk_min:.3g} min")
    c2.metric("Tsk", f"{sk.tsk_C:.4g} °C")
    c3.metric("T final", f"{sk.T_final_C:.4g} °C")
    with st.expander("Puntos calculados (para verificar Sk y Tsk a mano)"):
        df = item2.tabla_puntos_soaking(res, sk)
        st.dataframe(df, hide_index=True)
        descarga_csv(df, "item2c_puntos.csv")


cfg = configuracion()
st.title("Ítem 2 · Incorporación de efectos no lineales")
st.caption("Todos los casos se resuelven con RK2 y se comparan con la solución exacta del Ítem 1.")
seccion_ajuste(cfg)
t_a, t_b, t_c = st.tabs(["2a · C(T) variable", "2b · Radiación", "2c · Soaking"])
for pestaña, contenido in ((t_a, tab_2a), (t_b, tab_2b), (t_c, tab_2c)):
    with pestaña:
        contenido(cfg)
