"""Arma todas las figuras y tablas del TP con una misma configuración y las empaqueta en ZIP.

Lo usan la app (botones de descarga) y generar_resultados.py (carpeta resultados/).
Las figuras se exportan siempre con el estilo claro, pensado para el informe impreso.
"""

import io
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from calculos.datos import decisiones as D
from calculos.items import item1, item2, item3, item4, item5, item6
from calculos.items.configuracion import Configuracion
from calculos.modelo.calor_especifico import tabla
from calculos.modelo.simulacion import malla_analitica
from calculos.presentacion import graficos as G

ANCHO_PX, ALTO_PX, ESCALA_PNG = 1100, 550, 2


@dataclass(frozen=True)
class Entradas:
    """Todo lo que define los resultados: configuración, calibraciones y método del Ítem 5."""
    cfg: Configuracion = field(default_factory=Configuracion)
    escala_error: str = D.ESCALA_ERROR_RELATIVO
    cal3: item6.Calibracion | None = None
    cal4: item6.Calibracion | None = None
    opciones: item5.OpcionesMetodo = field(default_factory=item5.OpcionesMetodo)
    metodo: str = "Newton-Raphson"


def _figuras_item1(e: Entradas) -> dict[str, go.Figure]:
    res = item1.resolver(e.cfg)
    err = item1.errores(res, e.escala_error)
    curvas = [G.Curva("Analítica", res["analitica"].t_min, res["analitica"].T_C, "lines", G.SERIES[0]),
              G.Curva("Euler explícito", res["euler"].t_min, res["euler"].T_C, color=G.SERIES[1]),
              G.Curva("RK2", res["rk2"].t_min, res["rk2"].T_C, "markers", G.SERIES[2])]
    return {"item1a_evolucion": G.evolucion(curvas, "Ítem 1a – solo convección, h = cad"),
            "item1b_error_relativo": G.error_relativo(
                res["euler"].t_min, {"Euler explícito": err["euler"], "RK2": err["rk2"]}, e.escala_error)}


def _contra_exacta(cfg: Configuracion, res, nombre: str, titulo: str) -> go.Figure:
    exacta = malla_analitica(cfg.operacion_base(), cfg.c_medio())
    return G.evolucion([G.Curva("Exacta Ítem 1", exacta.t_min, exacta.T_C, "lines", G.SERIES[0]),
                        G.Curva(nombre, res.t_min, res.T_C, color=G.SERIES[1])], titulo)


def _figuras_item2(e: Entradas) -> dict[str, go.Figure]:
    cfg = e.cfg
    res, sk = item2.item2c(cfg)
    return {"item2a_ajustes_C": G.ajustes_calor(*tabla(cfg.tabla_c), item2.ajustes(cfg), cfg.grado_c),
            "item2a_evolucion": _contra_exacta(cfg, item2.item2a(cfg), "RK2 con C(T)", "Ítem 2a – C(T) variable"),
            "item2b_evolucion": _contra_exacta(cfg, item2.item2b(cfg), "RK2 con radiación", "Ítem 2b – radiación"),
            "item2c_soaking": G.soaking(res, sk, cfg.operacion_base(), "Ítem 2c – soaking")}


def _figuras_calibracion(e: Entradas) -> dict[str, go.Figure]:
    """Ítems 3 y 4, solo si ya tienen una calibración elegida o definida."""
    if e.cal3 is None:
        return {}
    op3 = e.cfg.operacion_base().con_temperaturas(e.cal3.T1_C, e.cal3.T2_C)
    res3, sk3 = item3.evaluar_operacion(e.cfg, op3)
    figs = {"item3_soaking": G.soaking(res3, sk3, op3, "Ítem 3 – calibración manual")}
    if e.cal4 is not None:
        op4 = item4.operacion_nueva(e.cfg, e.cal4.T1_C, e.cal4.T2_C)
        casos = [("Ítem 3", res3, sk3, op3), ("+15 % productividad", *item3.evaluar_operacion(e.cfg, op4), op4)]
        figs["item4_comparacion"] = G.comparar_operaciones(casos, "Ítem 4 – Ítem 3 vs nueva condición")
    return figs


def resolver_item5(e: Entradas) -> dict:
    """Resultado del método elegido para cada caso (A, B y C)."""
    return {caso: item5.resolver(e.cfg, tsk, e.metodo, e.opciones) for caso, tsk in item5.objetivos(e.cfg).items()}


def _figuras_item5(e: Entradas, resultados: dict) -> dict[str, go.Figure]:
    base, casos = e.cfg.operacion_base(), []
    for caso, r in resultados.items():
        if r.convergio:
            op = base.con_temperaturas(*r.x)
            casos.append((f"Caso {caso}", *item3.evaluar_operacion(e.cfg, op), op))
    figs = {"item5_convergencia": G.convergencia({f"Caso {c}": r.historial for c, r in resultados.items()},
                                                 e.opciones.tolerancias)}
    if casos:
        figs["item5_casos"] = G.comparar_operaciones(casos, f"Ítem 5 – casos A, B y C ({e.metodo})")
    return figs


def figuras(e: Entradas, resultados_item5: dict | None = None) -> dict[str, go.Figure]:
    resultados_item5 = resultados_item5 or resolver_item5(e)
    return (_figuras_item1(e) | _figuras_item2(e) | _figuras_calibracion(e)
            | _figuras_item5(e, resultados_item5))


def tablas(e: Entradas, resultados_item5: dict | None = None) -> dict[str, pd.DataFrame]:
    resultados_item5 = resultados_item5 or resolver_item5(e)
    res1 = item1.resolver(e.cfg)
    res2, sk = item2.item2c(e.cfg)
    dfs = {"item1b_puntos": item1.tabla_puntos(res1, item1.errores(res1, e.escala_error)),
           "item1c_estudio_paso": item1.estudio_paso(e.cfg, e.escala_error),
           "item2a_residuos": item2.tabla_ajustes(item2.ajustes(e.cfg)),
           "item2a_coeficientes": item2.tabla_coeficientes(e.cfg.ajuste_c()),
           "item2c_puntos": item2.tabla_puntos_soaking(res2, sk)}
    dfs |= {f"item5_caso_{c}_historial": item5.tabla_historial(r) for c, r in resultados_item5.items()}
    dfs["item6_resumen"] = item6.tabla_resumen(e.cfg, e.cal3, e.cal4, e.opciones, e.metodo)
    return dfs


def csv_bytes(df: pd.DataFrame) -> bytes:
    """CSV con BOM para que Excel muestre bien los acentos."""
    return df.to_csv(index=False).encode("utf-8-sig")


def _empaquetar(archivos: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in archivos.items():
            z.writestr(nombre, contenido)
    return buffer.getvalue()


def zip_tablas(dfs: dict[str, pd.DataFrame]) -> bytes:
    return _empaquetar({f"{nombre}.csv": csv_bytes(df) for nombre, df in dfs.items()})


def imagenes(figs: dict[str, go.Figure]) -> dict[str, bytes]:
    """PNG de cada figura (una sola sesión del navegador); sin navegador, HTML interactivo."""
    try:
        with tempfile.TemporaryDirectory() as carpeta:
            rutas = [Path(carpeta) / f"{nombre}.png" for nombre in figs]
            pio.write_images(list(figs.values()), rutas, width=ANCHO_PX, height=ALTO_PX, scale=ESCALA_PNG)
            return {ruta.name: ruta.read_bytes() for ruta in rutas}
    except Exception:  # kaleido necesita Chromium; sin él se entrega HTML
        return {f"{nombre}.html": fig.to_html(include_plotlyjs="cdn", config=G.CONFIG).encode("utf-8")
                for nombre, fig in figs.items()}


def zip_figuras(figs: dict[str, go.Figure]) -> bytes:
    return _empaquetar(imagenes(figs))
