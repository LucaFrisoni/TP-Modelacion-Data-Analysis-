"""Ítem 2: C(T) variable (2a), radiación (2b) y parámetros de soaking (2c), todo con RK2."""

import pandas as pd

from calculos.items.configuracion import Configuracion
from calculos.metodos.minimos_cuadrados import AjustePolinomico
from calculos.modelo.calor_especifico import todos_los_ajustes
from calculos.modelo.simulacion import Resultado, simular
from calculos.modelo.soaking import Soaking, calcular_soaking


def ajustes(cfg: Configuracion) -> list[AjustePolinomico]:
    return todos_los_ajustes(cfg.tabla_c)


def tabla_ajustes(lista: list[AjustePolinomico]) -> pd.DataFrame:
    return pd.DataFrame({"grado": [a.grado for a in lista],
                         "suma de cuadrados de residuos": [a.suma_cuadrados_residuos for a in lista],
                         "RMSE [J/kg K]": [a.rmse for a in lista]})


def tabla_coeficientes(ajuste: AjustePolinomico) -> pd.DataFrame:
    coef = ajuste.coeficientes()
    return pd.DataFrame({"término": [f"a{i} · T^{i}" for i in range(len(coef))], "coeficiente": coef})


def item2a(cfg: Configuracion) -> Resultado:
    """RK2 con C(T) del ajuste elegido, solo convección."""
    return simular(cfg.modelo(cfg.operacion_base(), radiacion=False, c_variable=True), "rk2")


def item2b(cfg: Configuracion) -> Resultado:
    """RK2 con convección + radiación y C promedio."""
    return simular(cfg.modelo(cfg.operacion_base(), radiacion=True, c_variable=False), "rk2")


def item2c(cfg: Configuracion) -> tuple[Resultado, Soaking]:
    """Sk y Tsk sobre los puntos calculados en el 2b."""
    res = item2b(cfg)
    return res, calcular_soaking(res.t_min, res.T_C, cfg.convencion_sk)


def tabla_puntos_soaking(res: Resultado, sk: Soaking) -> pd.DataFrame:
    return pd.DataFrame({"t [min]": res.t_min, "T [°C]": res.T_C, "en banda": sk.en_banda})
