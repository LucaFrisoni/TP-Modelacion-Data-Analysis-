"""Ítem 1: Euler explícito, RK2 y solución analítica con solo convección y C promedio."""

import numpy as np
import pandas as pd

from calculos.items.configuracion import Configuracion
from calculos.modelo.simulacion import (Resultado, error_relativo, malla_analitica, simular,
                                        solucion_analitica)


def resolver(cfg: Configuracion, subpasos: int = 1) -> dict[str, Resultado]:
    """Euler, RK2 y la analítica (en los nodos y en una malla fina para graficar)."""
    op = cfg.operacion_base()
    modelo = cfg.modelo(op, radiacion=False, c_variable=False)
    euler = simular(modelo, "euler", subpasos)
    return {
        "analitica": malla_analitica(op, cfg.c_medio()),
        "analitica_nodos": solucion_analitica(op, cfg.c_medio(), euler.t_s),
        "euler": euler,
        "rk2": simular(modelo, "rk2", subpasos),
    }


def errores(res: dict[str, Resultado], escala: str) -> dict[str, np.ndarray]:
    """Error relativo de Euler y RK2 respecto de la analítica, en K o en °C."""
    return {m: error_relativo(res[m], res["analitica_nodos"], escala) for m in ("euler", "rk2")}


def tabla_puntos(res: dict[str, Resultado], err: dict[str, np.ndarray]) -> pd.DataFrame:
    return pd.DataFrame({"t [min]": res["euler"].t_min, "Analítica [°C]": res["analitica_nodos"].T_C,
                         "Euler [°C]": res["euler"].T_C, "RK2 [°C]": res["rk2"].T_C,
                         "Error rel. Euler": err["euler"], "Error rel. RK2": err["rk2"]})


def estudio_paso(cfg: Configuracion, escala: str, subpasos=(1, 2, 4, 8)) -> pd.DataFrame:
    """Error final y máximo para h = cad, cad/2, ...; el cociente estima el orden (1c)."""
    filas = []
    for s in subpasos:
        res = resolver(cfg, s)
        for metodo, err in errores(res, escala).items():
            filas.append({"h [s]": cfg.operacion_base().cad_s / s, "método": metodo.upper(),
                          "T final [°C]": res[metodo].T_final_C,
                          "error relativo final": err[-1], "error relativo máximo": err.max()})
    df = pd.DataFrame(filas)
    df["cociente vs h anterior"] = df.groupby("método")["error relativo final"].transform(
        lambda e: e.shift(1) / e)
    return df
