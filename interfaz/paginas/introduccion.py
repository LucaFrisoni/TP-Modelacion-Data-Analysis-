"""Introducción: integrantes, consigna, planteo del problema, modelo, parámetros y mapa de los ítems."""

import pandas as pd
import streamlit as st

from calculos.datos import enunciado as E
from calculos.datos import grupo
from calculos.items import item4
from calculos.modelo import parametros as P
from calculos.modelo.calor_especifico import tabla
from interfaz.componentes.apariencia import RECURSOS
from interfaz.componentes.comun import configuracion, descarga_csv

_TABLA_NUM = {"Valor": st.column_config.NumberColumn(format="%.5g")}


def encabezado():
    st.html(f'<span class="tp-etiqueta">{grupo.MATERIA} · {grupo.CUATRIMESTRE} · FIUBA</span>')
    st.title("Revenido de tubos de acero en un horno continuo")
    st.html('<p class="tp-bajada">Métodos numéricos aplicados a la ingeniería de procesos: simulación '
            "térmica del tubo, ajuste de datos y calibración del horno.</p>")


def tarjeta_integrantes():
    filas = "".join(f'<div class="tp-integrante"><span>{nombre} <b>{apellido}</b></span>'
                    f'<span class="tp-padron">Padrón {padron}</span></div>'
                    for nombre, apellido, padron in grupo.INTEGRANTES)
    with st.container(border=True):
        st.markdown("**Integrantes**")
        st.html(filas)


def tarjeta_consigna():
    with st.container(border=True):
        st.markdown("**Consigna del TP**")
        st.markdown(f"Datos asignados al grupo: **NREF = {grupo.NREF}** y **tabla {grupo.TABLA_C}** "
                    "de calor específico.")
        st.download_button("Descargar consigna (PDF)", (RECURSOS / "consigna_tp.pdf").read_bytes,
                           file_name="Consigna TP 2C2026 - Revenido.pdf", mime="application/pdf",
                           icon=":material/description:", on_click="ignore", type="primary")


def seccion_problema():
    st.markdown(
        "El **revenido** es la última etapa del tratamiento de *temple y revenido* de tubos de acero para "
        "la industria petrolera: el tubo templado se recalienta hasta una temperatura objetivo (500–700 °C) "
        "y sus propiedades finales dependen de esa temperatura y del tiempo que permanece en ella.\n\n"
        f"Los tubos avanzan a velocidad constante por un **horno continuo de {E.L_HORNO:g} m** con "
        f"**{E.N_BOLSILLOS} bolsillos** (mecanismo *walking-beam*). La primera mitad del horno está a "
        "**T1** y la segunda a **T2**. El objetivo es predecir la temperatura del tubo y encontrar "
        "condiciones de operación que cumplan los objetivos metalúrgicos.")


def seccion_modelo(tiempo_min: float):
    st.subheader("Modelo térmico")
    st.markdown("Modelo de **temperatura uniforme** (todo el tubo a la misma T): balance de energía con "
                "convección y radiación desde el horno.")
    st.latex(r"-m\,C\,\frac{dT}{dt} = h_c S\,(T - T_\infty) + \sigma \varepsilon S\,(T^4 - T_\infty^4)")
    st.latex(r"S = \pi\,OD\,L_t \qquad m = \rho\,\pi\,OD\,WT\left(1 - \frac{WT}{OD}\right)L_t")
    st.latex(r"T_\infty(x) = \begin{cases} T_1 & x \le L/2 \\ T_2 & x > L/2 \end{cases}"
             r"\qquad x = v_0\,t \qquad v_0 = \frac{L}{n_{bol}\cdot cad}")
    st.markdown(
        f"La simulación termina cuando el tubo sale del horno: $t_f = L / v_0 = n_{{bol}}\\cdot cad$ "
        f"= **{tiempo_min:.4g} min**. Este tiempo no figura explícito en el enunciado: se deduce del recorrido.\n\n"
        "Condición inicial: $T(0) = 20$ °C. Los cálculos se hacen en **K y s** y los resultados se muestran "
        "en **°C y min**, como pide el enunciado.")


def seccion_metodos():
    st.subheader("Métodos de discretización")
    st.markdown("Se usan en todos los ítems con paso $h = cad$ (el Ítem 1 compara ambos; del 2 en adelante, RK2).")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Euler explícito**")
        st.latex(r"u_{n+1} = u_n + h\,f(u_n, t_n)")
    with c2:
        st.markdown("**Runge-Kutta de 2.º orden (RK2)**")
        st.latex(r"\begin{aligned} q_1 &= h\,f(u_n, t_n) \\ q_2 &= h\,f(u_n + q_1, t_{n+1}) \\"
                 r" u_{n+1} &= u_n + \tfrac{1}{2}(q_1 + q_2) \end{aligned}")


def tablas_parametros(cfg) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    op = cfg.operacion_base()
    fijos = [("ρ", E.RHO, "kg/m³"), ("OD", E.OD * 1e3, "mm"), ("WT", E.WT * 1e3, "mm"), ("Lt", E.LT, "m"),
             ("L", E.L_HORNO, "m"), ("n° bolsillos", E.N_BOLSILLOS, "—"), ("hc", E.HC, "W/m² K"),
             ("σ", E.SIGMA, "W/m² K⁴"), ("ε", E.EPSILON, "—"), ("T inicial", E.T0_C, "°C")]
    proceso = [("cad = 10 s·NREF + 25 s", op.cad_s, "s"), ("T1 = T2 = 150 °C·NREF + 550 °C", op.T1_C, "°C")]
    derivados = [("Masa m", P.masa_kg(), "kg"), ("Superficie S", P.superficie_m2(), "m²"),
                 ("Velocidad v0", P.velocidad_m_s(op.cad_s), "m/s"),
                 ("Tiempo en el horno", P.tiempo_en_horno_s(op.cad_s) / 60, "min"),
                 (f"C promedio (tabla {cfg.tabla_c})", cfg.c_medio(), "J/kg K"),
                 ("τ = mC/(hc S) (solo convección)", P.constante_tiempo_conveccion_s(cfg.c_medio()) / 60, "min")]
    columnas = ["Parámetro", "Valor", "Unidad"]
    return tuple(pd.DataFrame(f, columns=columnas) for f in (fijos, proceso, derivados))


def seccion_parametros(cfg):
    st.subheader(f"Parámetros del grupo (NREF = {cfg.nref:g}, tabla {cfg.tabla_c})")
    fijos, proceso, derivados = tablas_parametros(cfg)
    c1, c2, c3 = st.columns(3)
    for col, titulo, df in ((c1, "Datos del enunciado", fijos), (c2, "Proceso (según NREF)", proceso),
                            (c3, "Calculados", derivados)):
        col.markdown(f"**{titulo}**")
        col.dataframe(df, hide_index=True, column_config=_TABLA_NUM)
    T, C = tabla(cfg.tabla_c)
    with c2:
        st.markdown(f"**Tabla {cfg.tabla_c} de calor específico**")
        st.dataframe(pd.DataFrame({"T [°C]": T, "C [J/kg K]": C}), hide_index=True)
    descarga_csv(pd.concat([fijos, proceso, derivados]), "parametros.csv", "Descargar parámetros")


def mapa_items(cfg) -> pd.DataFrame:
    cad, cad4 = f"{cfg.operacion_base().cad_s:g} s", f"{item4.cadencia_nueva_s(cfg):.4g} s"
    T = f"T1 = T2 = {cfg.operacion_base().T1_C:g} °C"
    filas = [
        ("1", "Euler vs RK2 vs solución exacta", "Convección", "Promedio", T, cad, "Euler y RK2"),
        ("2a", "¿Influye C(T)?", "Convección", "Ajuste C(T)", T, cad, "RK2"),
        ("2b", "¿Influye la radiación?", "Convección + radiación", "Promedio", T, cad, "RK2"),
        ("2c", "Sk y Tsk", "Convección + radiación", "Promedio", T, cad, "RK2"),
        ("3", "Calibración manual: Sk = 10 min, Tsk del 2c", "Convección + radiación", "Ajuste C(T)",
         "T1 y T2 a calibrar", cad, "RK2"),
        ("4", "+15 % de productividad", "Convección + radiación", "Ajuste C(T)", "T1 y T2 a calibrar", cad4, "RK2"),
        ("5", "Calibración automática, casos A, B y C", "Convección + radiación", "Ajuste C(T)",
         "T1 y T2 = incógnitas", cad, "RK2 + NR / secante / punto fijo"),
        ("6", "Síntesis de resultados", "—", "—", "—", "—", "—"),
    ]
    return pd.DataFrame(filas, columns=["Ítem", "Qué se busca", "Calor", "C", "Horno", "Cadencia", "Método"])


cfg = configuracion()
encabezado()
c1, c2 = st.columns([3, 2])
with c1:
    tarjeta_integrantes()
with c2:
    tarjeta_consigna()
st.subheader("El problema")
seccion_problema()
seccion_modelo(P.tiempo_en_horno_s(cfg.operacion_base().cad_s) / 60)
seccion_metodos()
seccion_parametros(cfg)
st.subheader("Cómo cambia el planteo en cada ítem")
st.caption("Cada página empieza con un recuadro que detalla las ecuaciones y datos propios de ese ítem.")
st.dataframe(mapa_items(cfg), hide_index=True)
st.caption("Gráficos: el ícono de cámara (arriba a la derecha de cada gráfico) descarga uno en PNG. "
           "Desde el panel lateral se descargan todas las figuras y tablas juntas.")
