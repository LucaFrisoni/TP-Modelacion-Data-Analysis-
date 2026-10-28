"""Ítem 6: tabla resumen de resultados con 3 cifras significativas."""

from dataclasses import dataclass

import pandas as pd

from calculos.items import item1, item2, item5
from calculos.items.configuracion import Configuracion
from calculos.presentacion.formato import texto_cifras as f3

SIN_CALIBRAR = "Sin calibrar"
COLUMNAS = ["Ítem", "Magnitud", "Unidad", "Resultado", "Origen"]


@dataclass(frozen=True)
class Calibracion:
    """Resultado (T1, T2) de una calibración manual y de dónde proviene."""

    T1_C: float
    T2_C: float
    origen: str


def _filas_item1(cfg: Configuracion) -> list[tuple]:
    r = item1.resolver(cfg)
    return [("1", f"Temperatura final del tubo – {nombre}", "°C", f3(r[clave].T_final_C), "Modelo")
            for nombre, clave in (("solución analítica", "analitica"), ("Euler explícito", "euler"),
                                  ("RK2", "rk2"))]


def _filas_item2(cfg: Configuracion) -> list[tuple]:
    _, sk = item2.item2c(cfg)
    return [("2b", "Tiempo de soaking (Sk), convección + radiación", "min", f3(sk.sk_min), "Modelo"),
            ("2b", "Temperatura de soaking (Tsk)", "°C", f3(sk.tsk_C), "Modelo")]


def _filas_calibracion(item: str, cal: Calibracion | None) -> list[tuple]:
    if cal is None:
        return [(item, f"T{i}", "°C", SIN_CALIBRAR, "—") for i in (1, 2)]
    return [(item, "T1", "°C", f3(cal.T1_C), cal.origen), (item, "T2", "°C", f3(cal.T2_C), cal.origen)]


def _filas_item5(cfg: Configuracion, opciones: item5.OpcionesMetodo, metodo: str) -> list[tuple]:
    filas = []
    for caso, tsk in item5.objetivos(cfg).items():
        r = item5.resolver(cfg, tsk, metodo, opciones)
        if not r.convergio:
            filas.append((f"5{caso}", "T1 y T2", "°C", "No convergió", metodo))
            continue
        iter_txt = "iteración" if r.iteraciones == 1 else "iteraciones"
        origen = f"{metodo} · {r.iteraciones} {iter_txt}"
        filas += [(f"5{caso}", f"T{i + 1}", "°C", f3(r.x[i]), origen) for i in (0, 1)]
    return filas


def tabla_resumen(cfg: Configuracion, cal3: Calibracion | None, cal4: Calibracion | None,
                  opciones: item5.OpcionesMetodo, metodo: str = "Newton-Raphson") -> pd.DataFrame:
    filas = (_filas_item1(cfg) + _filas_item2(cfg) + _filas_calibracion("3", cal3)
             + _filas_calibracion("4", cal4) + _filas_item5(cfg, opciones, metodo))
    return pd.DataFrame(filas, columns=COLUMNAS)
