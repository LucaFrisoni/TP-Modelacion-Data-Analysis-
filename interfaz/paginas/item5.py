"""Ítem 5: calibración automática resolviendo F(T1, T2) = 0 con NR, secante y punto fijo."""

import pandas as pd
import streamlit as st

from calculos.items import item3, item5
from calculos.presentacion import graficos as G
from interfaz.componentes import opciones_item5
from interfaz.componentes.comun import configuracion, descarga_csv, grafico, planteo

_FORMATO = {c: st.column_config.NumberColumn(format="%.4g") for c in ("T1 [°C]", "T2 [°C]", "F1 [°C]", "F2 [min]")}


@st.cache_data(show_spinner="Resolviendo…")
def resolver(cfg, tsk_obj, metodo, opciones):
    return item5.resolver(cfg, tsk_obj, metodo, opciones)


def seccion_planteo(cfg, objetivos):
    planteo(
        "Planteo del Ítem 5",
        "Se automatiza el Ítem 3: T1 y T2 son las incógnitas de un sistema no lineal cuyas funciones son el "
        f"modelo completo (radiación + C(T)), con la cadencia original ({cfg.operacion_base().cad_s:g} s). "
        "Cada evaluación de F es una simulación completa. Tsk objetivo: "
        + ", ".join(f"caso {c} = **{t:.4g} °C**" for c, t in objetivos.items()) + "; Sk objetivo = 10 min.",
        (r"F_1(T_1,T_2) = T_{sk}(T_1,T_2) - T_{sk,obj} = 0 \qquad F_2(T_1,T_2) = S_k(T_1,T_2) - S_{k,obj} = 0",
         r"\begin{bmatrix}T_1\\T_2\end{bmatrix}^{(k+1)} = \begin{bmatrix}T_1\\T_2\end{bmatrix}^{(k)}"
         r" - J^{-1}\begin{bmatrix}F_1\\F_2\end{bmatrix}^{(k)}",
         r"J_{NR} = \left[\frac{\partial F_i}{\partial T_j}\right] \qquad "
         r"J_{SEC} = \left[\frac{F_i^{(k)} - F_i^{(k-1)}}{T_j^{(k)} - T_j^{(k-1)}}\right] \qquad "
         r"J_{PF} = I"))
    st.caption("NR: J por diferencias finitas con paso Δ. Secante (Broyden): J inicial por diferencias finitas "
               "y luego actualizaciones de rango 1. Secante (enunciado): J_SEC tal cual figura en la consigna.")


def fila_resultado(metodo, r) -> dict:
    return {"método": metodo, "convergió": "Sí" if r.convergio else "No", "iteraciones": r.iteraciones,
            "simulaciones": r.evaluaciones, "T1 [°C]": r.x[0], "T2 [°C]": r.x[1],
            "F1 [°C]": r.historial[-1].F[0], "F2 [min]": r.historial[-1].F[1], "detalle": r.mensaje}


def historiales(caso, resultados):
    descarga_csv(item5.tabla_historiales(resultados), f"item5_caso_{caso}_historiales.csv",
                 "Descargar historial de todos los métodos", clave=f"dl_{caso}")
    for m, r in resultados.items():
        with st.expander(f"Historial de iteraciones · {m}"):
            df = item5.tabla_historial(r)
            st.dataframe(df, hide_index=True)
            descarga_csv(df, f"item5_caso_{caso}_{m}.csv", clave=f"dl_{caso}_{m}")


def seccion_caso(cfg, caso, tsk_obj, metodos, op):
    x0 = op.x0(tsk_obj)
    st.markdown(f"**Objetivo:** Tsk = {tsk_obj:.4g} °C, Sk = 10 min · valor inicial "
                f"(T1, T2) = ({x0[0]:.4g}, {x0[1]:.4g}) °C")
    resultados = {m: resolver(cfg, tsk_obj, m, op) for m in metodos}
    st.dataframe(pd.DataFrame([fila_resultado(m, r) for m, r in resultados.items()]), hide_index=True,
                 column_config=_FORMATO)
    grafico(G.convergencia({m: r.historial for m, r in resultados.items()}, op.tolerancias), clave=f"conv_{caso}")
    historiales(caso, resultados)
    return resultados


def grafico_final(cfg, todos, metodo):
    casos, base = [], cfg.operacion_base()
    for caso, resultados in todos.items():
        r = resultados.get(metodo)
        if r is None or not r.convergio:
            st.warning(f"Caso {caso}: {metodo} no convergió, no se grafica.", icon=":material/warning:")
            continue
        op = base.con_temperaturas(*r.x)
        casos.append((f"Caso {caso}", *item3.evaluar_operacion(cfg, op), op))
    if casos:
        grafico(G.comparar_operaciones(casos, f"Ítem 5 – evolución térmica de los casos ({metodo})"))


def seccion_casos(cfg, objetivos, metodos, opciones):
    todos = {}
    for caso, tab in zip(objetivos, st.tabs([f"Caso {c}" for c in objetivos])):
        with tab:
            todos[caso] = seccion_caso(cfg, caso, objetivos[caso], metodos, opciones)
    st.subheader("Evolución térmica de los casos A, B y C")
    grafico_final(cfg, todos, st.selectbox("Método para el gráfico", metodos))


cfg = configuracion()
objetivos = item5.objetivos(cfg)
st.title("Ítem 5 · Calibración automática (sistema no lineal)")
seccion_planteo(cfg, objetivos)
st.subheader("Configuración de los métodos")
nombre, opciones = opciones_item5.seleccionar()
metodos = st.pills("Métodos a comparar", item5.METODOS, selection_mode="multi", default=list(item5.METODOS))
if metodos:
    seccion_casos(cfg, objetivos, metodos, opciones)
else:
    st.info("Elegí al menos un método.", icon=":material/info:")
