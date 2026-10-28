"""Descargas globales: todas las figuras (PNG) y todas las tablas (CSV) del TP, cada grupo en un ZIP."""

import pandas as pd
import streamlit as st

from calculos import reporte
from calculos.datos import decisiones as D
from interfaz.componentes import resultados_sesion
from interfaz.componentes.comun import configuracion

CLAVE_ESCALA, CLAVE_METODO = "escala_error", "metodo_item6"
_AYUDA = ("Las figuras salen con el estilo claro, para el informe. Los Ítems 3 y 4 se incluyen cuando tienen "
          "resultado elegido, junto con sus iteraciones; el Ítem 5 usa la configuración activa y el método elegido en el Ítem 6.")


def entradas_sesion() -> reporte.Entradas:
    """Los resultados tal como se ven en la app: decisiones del panel, calibraciones y Ítem 5 activo."""
    _, opciones = resultados_sesion.opciones_activas()
    return reporte.Entradas(cfg=configuracion(),
                            escala_error=st.session_state.get(CLAVE_ESCALA, D.ESCALA_ERROR_RELATIVO),
                            cal3=resultados_sesion.calibracion("3"), cal4=resultados_sesion.calibracion("4"),
                            opciones=opciones, metodo=st.session_state.get(CLAVE_METODO, "Newton-Raphson"))


def iteraciones_manuales() -> dict[str, pd.DataFrame]:
    """Iteraciones de calibración manual de los Ítems 3 y 4 registradas en la sesión."""
    return {f"item{n}_iteraciones": pd.DataFrame(st.session_state[f"item{n}_historial"])
            for n in ("3", "4") if st.session_state.get(f"item{n}_historial")}


def botones():
    """Los ZIP se generan recién al hacer clic (no demoran la página)."""
    e, iteraciones = entradas_sesion(), iteraciones_manuales()
    st.download_button("Todas las figuras (PNG)", lambda: reporte.zip_figuras(reporte.figuras(e)),
                       file_name="figuras_tp_revenido.zip", mime="application/zip",
                       icon=":material/image:", on_click="ignore", width="stretch")
    st.download_button("Todas las tablas (CSV)", lambda: reporte.zip_tablas(reporte.tablas(e) | iteraciones),
                       file_name="tablas_tp_revenido.zip", mime="application/zip",
                       icon=":material/table_view:", on_click="ignore", width="stretch")
    st.caption("Con las decisiones y calibraciones actuales.", help=_AYUDA)
