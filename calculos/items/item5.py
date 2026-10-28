"""Ítem 5: calibración automática resolviendo F(T1, T2) = 0 con NR, secante y punto fijo."""

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from calculos.datos import decisiones as D
from calculos.datos import enunciado as E
from calculos.items import item3
from calculos.items.configuracion import Configuracion
from calculos.metodos import sistemas_no_lineales as snl

METODOS = ("Newton-Raphson", "Secante (Broyden)", "Secante (enunciado)", "Punto fijo")


@dataclass(frozen=True)
class OpcionesMetodo:
    """Parámetros de los métodos iterativos. Los valores por defecto salen de decisiones.py."""

    delta_C: float = D.DELTA_JACOBIANO_C
    desplazamiento_inicial_C: tuple[float, float] = D.DESPLAZAMIENTO_INICIAL_C
    tolerancias: tuple[float, float] = (D.TOL_F1_C, D.TOL_F2_MIN)
    max_iteraciones: int = D.MAX_ITERACIONES
    rango_fisico_C: tuple[float, float] = D.RANGO_FISICO_C
    J_punto_fijo: tuple[tuple[float, float], tuple[float, float]] = ((1.0, 0.0), (0.0, 1.0))
    # TODO: VALIDAR FÓRMULA O CRITERIO — subpasos > 1 usa h < cad para que Sk varíe en
    # escalones más finos; el enunciado solo fija h = cad en el Ítem 1.
    subpasos: int = 1
    amortiguado: bool = D.AMORTIGUAR_PASO

    def criterio(self) -> snl.Criterio:
        return snl.Criterio(self.tolerancias, self.max_iteraciones, self.rango_fisico_C, self.amortiguado)

    def x0(self, tsk_obj: float) -> np.ndarray:
        return tsk_obj + np.asarray(self.desplazamiento_inicial_C, float)

    def a_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def desde_dict(cls, datos: dict) -> "OpcionesMetodo":
        """Reconstruye las opciones desde JSON (las listas vuelven a ser tuplas)."""
        desconocidos = set(datos) - set(cls.__dataclass_fields__)
        if desconocidos:
            raise ValueError(f"Campos desconocidos en la configuración: {sorted(desconocidos)}")
        return cls(**{k: _a_tupla(v) for k, v in datos.items()})


def _a_tupla(valor):
    return tuple(_a_tupla(v) for v in valor) if isinstance(valor, list) else valor


def objetivos(cfg: Configuracion) -> dict[str, float]:
    """Tsk objetivo de los casos A, B y C (Sk objetivo = 10 min en los tres)."""
    return {"A": item3.tsk_objetivo(cfg),
            "B": E.tsk_objetivo_caso_c(cfg.nref, "B"),
            "C": E.tsk_objetivo_caso_c(cfg.nref, "C")}


def sistema(cfg: Configuracion, tsk_obj: float, subpasos: int = 1):
    """F(T1, T2) = [Tsk(T1, T2) - Tsk_obj, Sk(T1, T2) - Sk_obj] con la cadencia original."""
    op = cfg.operacion_base()

    def F(x):
        _, sk = item3.evaluar_operacion(cfg, op.con_temperaturas(x[0], x[1]), subpasos)
        return np.array([sk.tsk_C - tsk_obj, sk.sk_min - E.SK_OBJETIVO_MIN])
    return F


def resolver(cfg: Configuracion, tsk_obj: float, metodo: str,
             op: OpcionesMetodo = OpcionesMetodo()) -> snl.ResultadoIterativo:
    F, x0, crit = sistema(cfg, tsk_obj, op.subpasos), op.x0(tsk_obj), op.criterio()
    if metodo == "Newton-Raphson":
        return snl.newton_raphson(F, x0, crit, op.delta_C)
    if metodo == "Secante (Broyden)":
        return snl.secante_broyden(F, x0, crit, op.delta_C)
    if metodo == "Secante (enunciado)":
        return snl.secante_enunciado(F, x0, x0 - np.array([op.delta_C, 2 * op.delta_C]), crit)
    if metodo == "Punto fijo":
        return snl.punto_fijo(F, x0, crit, op.J_punto_fijo)
    raise ValueError(f"Método {metodo!r} desconocido. Opciones: {METODOS}")


def tabla_historial(res: snl.ResultadoIterativo) -> pd.DataFrame:
    return pd.DataFrame([{"k": it.k, "T1 [°C]": it.x[0], "T2 [°C]": it.x[1],
                          "F1 = Tsk - obj [°C]": it.F[0], "F2 = Sk - obj [min]": it.F[1]}
                         for it in res.historial])


def tabla_historiales(resultados: dict[str, snl.ResultadoIterativo]) -> pd.DataFrame:
    """Historial de todos los métodos en una sola tabla (columna "método")."""
    return pd.concat([tabla_historial(r).assign(método=m) for m, r in resultados.items()],
                     ignore_index=True)
