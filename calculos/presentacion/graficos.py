"""Gráficos interactivos (Plotly) con estilo uniforme, en °C y minutos, listos para el informe."""

from dataclasses import dataclass

import numpy as np
import plotly.graph_objects as go

from calculos.metodos.minimos_cuadrados import AjustePolinomico
from calculos.modelo.parametros import Operacion, tiempo_en_horno_s
from calculos.modelo.simulacion import Resultado
from calculos.modelo.soaking import Soaking

# Paleta categórica validada (orden fijo, nunca se cicla) y colores neutros del tema claro.
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6")
TEXTO, TEXTO_SEC, GRILLA, FONDO = "#2a1712", "#5a4a45", "#ebe5e1", "#ffffff"
NEUTRO, BANDA = "#8f8784", "rgba(143,135,132,0.16)"

# Equivalentes del tema oscuro: mismos tonos, con el paso validado sobre la superficie oscura.
_SERIES_OSCURO = ("#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9")
_A_OSCURO = dict(zip(SERIES, _SERIES_OSCURO)) | {
    TEXTO: "#f1ece9", TEXTO_SEC: "#c9bfbb", GRILLA: "#352a27", FONDO: "#1a1413"}

# Configuración de la barra de Plotly: la cámara descarga PNG en alta resolución.
CONFIG = {"displaylogo": False,
          "toImageButtonOptions": {"format": "png", "scale": 3, "filename": "grafico_tp"}}


@dataclass(frozen=True)
class Curva:
    nombre: str
    t_min: np.ndarray
    T_C: np.ndarray
    modo: str = "lines+markers"   # "lines" para curvas continuas (analítica)
    color: str = SERIES[0]


def _estilo(fig: go.Figure, titulo: str, eje_x: str, eje_y: str) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16, color=TEXTO)), template="plotly_white",
        paper_bgcolor=FONDO, plot_bgcolor=FONDO, font=dict(family="Inter, Arial", size=13, color=TEXTO_SEC),
        legend=dict(orientation="h", yanchor="top", y=-0.16, x=0), hovermode="x unified",
        margin=dict(l=70, r=30, t=60, b=130), height=540)
    for eje, texto in ((fig.update_xaxes, eje_x), (fig.update_yaxes, eje_y)):
        eje(title_text=texto, gridcolor=GRILLA, zeroline=False, linecolor=NEUTRO, showline=True)
    return fig


def _traza(c: Curva) -> go.Scatter:
    return go.Scatter(x=c.t_min, y=c.T_C, name=c.nombre, mode=c.modo,
                      line=dict(color=c.color, width=2), marker=dict(size=8, color=c.color),
                      hovertemplate="%{y:.2f} °C<extra>" + c.nombre + "</extra>")


def evolucion(curvas: list[Curva], titulo: str) -> go.Figure:
    fig = go.Figure([_traza(c) for c in curvas])
    return _estilo(fig, titulo, "Tiempo [min]", "Temperatura del tubo [°C]")


def error_relativo(t_min: np.ndarray, errores: dict[str, np.ndarray], escala: str,
                   logaritmico: bool = True) -> go.Figure:
    """Error relativo de cada método (se omite t = 0, donde el error es nulo).

    La escala log permite ver a Euler y RK2 juntos aunque difieran en órdenes de magnitud.
    """
    fig = go.Figure()
    for i, (nombre, err) in enumerate(errores.items()):
        fig.add_trace(go.Scatter(x=t_min[1:], y=err[1:], name=nombre, mode="lines+markers",
                                 line=dict(color=SERIES[i + 1], width=2), marker=dict(size=8),
                                 hovertemplate="%{y:.3e}<extra>" + nombre + "</extra>"))
    unidad = "K" if escala == "K" else "°C"
    eje = "Error relativo [-]" + (" (escala log)" if logaritmico else "")
    _estilo(fig, f"Error relativo respecto de la solución exacta (temperaturas en {unidad})",
            "Tiempo [min]", eje)
    return fig.update_yaxes(type="log" if logaritmico else "linear", exponentformat="power")


def ajustes_calor(T_tab, C_tab, ajustes: list[AjustePolinomico], grado_elegido: int) -> go.Figure:
    """Todos los polinomios de mínimos cuadrados sobre los puntos de la tabla."""
    T = np.linspace(min(T_tab), max(T_tab), 300)
    fig = go.Figure()
    for a in ajustes:
        elegido = a.grado == grado_elegido
        fig.add_trace(go.Scatter(
            x=T, y=a(T), name=f"Grado {a.grado}" + (" (elegido)" if elegido else ""), mode="lines",
            line=dict(color=SERIES[a.grado % len(SERIES)], width=4 if elegido else 1.6),
            opacity=1.0 if elegido else 0.75, hovertemplate="%{y:.1f} J/kg K"))
    fig.add_trace(go.Scatter(x=T_tab, y=C_tab, name="Tabla", mode="markers",
                             marker=dict(size=10, color=TEXTO, symbol="circle")))
    return _estilo(fig, "Ajustes por mínimos cuadrados de C(T)", "Temperatura [°C]",
                   "Calor específico [J/kg K]")


def perfil_horno(op: Operacion) -> tuple[np.ndarray, np.ndarray]:
    """Temperatura del horno T∞ vista por el tubo en función del tiempo (escalón en L/2)."""
    t_fin = tiempo_en_horno_s(op.cad_s) / 60
    return (np.array([0, t_fin / 2, t_fin / 2, t_fin]),
            np.array([op.T1_C, op.T1_C, op.T2_C, op.T2_C]))


def _agregar_horno(fig: go.Figure, op: Operacion, nombre: str, color: str):
    t, T = perfil_horno(op)
    fig.add_trace(go.Scatter(x=t, y=T, name=nombre, mode="lines", hoverinfo="skip",
                             line=dict(color=color, width=1.5, dash="dash")))


def soaking(res: Resultado, sk: Soaking, op: Operacion, titulo: str) -> go.Figure:
    """Evolución térmica con la banda de soaking, los puntos en banda y el horno."""
    fig = evolucion([Curva("Tubo (RK2)", res.t_min, res.T_C)], titulo)
    fig.add_hrect(y0=sk.limite_inferior_C, y1=sk.T_final_C, fillcolor=BANDA, line_width=0)
    fig.add_trace(go.Scatter(x=res.t_min[sk.en_banda], y=res.T_C[sk.en_banda], name="Puntos en banda",
                             mode="markers", marker=dict(size=11, color=SERIES[1],
                                                         line=dict(width=2, color=FONDO))))
    _agregar_horno(fig, op, "Horno T∞", NEUTRO)
    fig.add_hline(y=sk.tsk_C, line=dict(color=SERIES[2], width=1.5, dash="dot"))
    texto = (f"Sk = {sk.sk_min:.3g} min<br>Tsk = {sk.tsk_C:.4g} °C<br>"
             f"T final = {sk.T_final_C:.4g} °C<br>T1 = {op.T1_C:.4g} °C, T2 = {op.T2_C:.4g} °C")
    fig.add_annotation(text=texto, xref="paper", yref="paper", x=0.98, y=0.04, xanchor="right",
                       yanchor="bottom", showarrow=False, align="left", bgcolor=FONDO,
                       bordercolor=GRILLA, font=dict(color=TEXTO))
    return fig


def comparar_operaciones(casos: list[tuple[str, Resultado, Soaking, Operacion]], titulo: str) -> go.Figure:
    """Varias operaciones superpuestas: curva del tubo y perfil del horno del mismo color."""
    fig = go.Figure()
    for i, (nombre, res, sk, op) in enumerate(casos):
        color = SERIES[i % len(SERIES)]
        etiqueta = f"{nombre}: Sk = {sk.sk_min:.3g} min, Tsk = {sk.tsk_C:.4g} °C"
        fig.add_trace(_traza(Curva(etiqueta, res.t_min, res.T_C, color=color)))
        _agregar_horno(fig, op, f"{nombre}: horno (T1 = {op.T1_C:.4g}, T2 = {op.T2_C:.4g} °C)", color)
    return _estilo(fig, titulo, "Tiempo [min]", "Temperatura [°C]")


def convergencia(historiales: dict[str, list], tolerancias: tuple[float, float]) -> go.Figure:
    """Residuo escalado ||F / tol|| por iteración; por debajo de 1 se cumplen ambas tolerancias."""
    fig = go.Figure()
    for i, (nombre, hist) in enumerate(historiales.items()):
        r = [np.linalg.norm(it.F / np.asarray(tolerancias)) for it in hist]
        fig.add_trace(go.Scatter(x=[it.k for it in hist], y=r, name=nombre, mode="lines+markers",
                                 line=dict(color=SERIES[i], width=2), marker=dict(size=8)))
    fig.add_hline(y=1.0, line=dict(color=NEUTRO, dash="dash"))
    _estilo(fig, "Convergencia: residuo escalado por iteración", "Iteración k", "‖F / tol‖ (escala log)")
    return fig.update_yaxes(type="log").update_layout(hovermode="closest")


def _recolorear(valor, mapa: dict):
    if isinstance(valor, dict):
        return {k: _recolorear(v, mapa) for k, v in valor.items()}
    if isinstance(valor, list):
        return [_recolorear(v, mapa) for v in valor]
    return mapa.get(valor, valor) if isinstance(valor, str) else valor


def version_oscura(fig: go.Figure) -> go.Figure:
    """Copia de la figura para el tema oscuro: cambia cada color claro por su par oscuro."""
    oscura = go.Figure(_recolorear(fig.to_dict(), _A_OSCURO))
    return oscura.update_layout(template="plotly_dark", paper_bgcolor=_A_OSCURO[FONDO],
                                plot_bgcolor=_A_OSCURO[FONDO])
