"""Ítem 4: nueva condición con +15 % de productividad, partiendo del resultado del Ítem 3."""

import streamlit as st

from calculos.datos import enunciado as E
from calculos.items import item3, item4
from calculos.modelo.parametros import tiempo_en_horno_s
from calculos.presentacion import graficos as G
from interfaz.componentes import calibracion_manual, resultados_sesion
from interfaz.componentes.comun import configuracion, grafico, planteo


def seccion_planteo(cfg, cad_nueva: float):
    cad = cfg.operacion_base().cad_s
    planteo(
        "Planteo del Ítem 4",
        f"Productividad = tubos por unidad de tiempo ∝ 1/cad. Para +{E.INCREMENTO_PRODUCTIVIDAD:.0%}: "
        f"cad = **{cad:g} s → {cad_nueva:.4g} s**, y el tiempo en el horno pasa de "
        f"{tiempo_en_horno_s(cad) / 60:.4g} a **{tiempo_en_horno_s(cad_nueva) / 60:.4g} min**. "
        "Hay que encontrar nuevas T1 y T2 que mantengan Sk y Tsk dentro de las tolerancias del Ítem 3.",
        (r"cad_{nueva} = \frac{cad}{1 + 0{,}15}",))


def seccion_condicion_item3(cal):
    st.subheader("Condición del Ítem 3")
    c1, c2, c3 = st.columns(3)
    c1.metric("T1", f"{cal.T1_C:g} °C")
    c2.metric("T2", f"{cal.T2_C:g} °C")
    c3.metric("Origen", cal.origen)


def seccion_nueva_condicion(cfg, cal3):
    tsk_obj = item3.tsk_objetivo(cfg)
    op_orig = cfg.operacion_base().con_temperaturas(cal3.T1_C, cal3.T2_C)
    res_o, sk_o = item3.evaluar_operacion(cfg, op_orig)
    st.subheader("Nueva condición")
    op_n, res_n, sk_n = calibracion_manual.panel("4", cfg, item4.operacion_nueva(cfg, cal3.T1_C, cal3.T2_C),
                                                 tsk_obj, (cal3.T1_C, cal3.T2_C))
    st.subheader("Comparación")
    casos = [("Ítem 3", res_o, sk_o, op_orig), ("+15 % productividad", res_n, sk_n, op_n)]
    grafico(G.comparar_operaciones(casos, "Ítem 4 – condición del Ítem 3 vs nueva condición"))


cfg = configuracion()
st.title("Ítem 4 · Incremento de productividad")
cad_nueva = item4.cadencia_nueva_s(cfg)
seccion_planteo(cfg, cad_nueva)
cal3 = resultados_sesion.calibracion("3")
if cal3 is None:
    st.info("Todavía no hay resultado del Ítem 3. Calibralo y tocá **Usar como resultado del Ítem 3**.",
            icon=":material/info:")
else:
    seccion_condicion_item3(cal3)
    seccion_nueva_condicion(cfg, cal3)
