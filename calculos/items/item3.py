"""Ítem 3: modelo completo (radiación + C(T)) y verificación del objetivo de calibración.

Lo reutilizan los Ítems 4 y 5, que trabajan con el mismo modelo.
"""

from dataclasses import dataclass

from calculos.datos import enunciado as E
from calculos.items import item2
from calculos.items.configuracion import Configuracion
from calculos.modelo.parametros import Operacion
from calculos.modelo.simulacion import Resultado, simular
from calculos.modelo.soaking import Soaking, calcular_soaking


def evaluar_operacion(cfg: Configuracion, op: Operacion, subpasos: int = 1) -> tuple[Resultado, Soaking]:
    """Simula una operación con el modelo completo y calcula Sk y Tsk."""
    res = simular(cfg.modelo(op, radiacion=True, c_variable=True), "rk2", subpasos)
    return res, calcular_soaking(res.t_min, res.T_C, cfg.convencion_sk)


@dataclass(frozen=True)
class Verificacion:
    sk_ok: bool
    tsk_ok: bool

    @property
    def cumple(self) -> bool:
        return self.sk_ok and self.tsk_ok


def verificar_objetivo(sk: Soaking, tsk_objetivo_C: float) -> Verificacion:
    """Tolerancias del Ítem 3: Sk = 10 ± 1 min y Tsk = objetivo ± 2 °C."""
    return Verificacion(abs(sk.sk_min - E.SK_OBJETIVO_MIN) <= E.TOL_SK_MIN,
                        abs(sk.tsk_C - tsk_objetivo_C) <= E.TOL_TSK_C)


def tsk_objetivo(cfg: Configuracion) -> float:
    """El Ítem 3 pide mantener el Tsk calculado en el Ítem 2c."""
    return item2.item2c(cfg)[1].tsk_C


def registrar_iteracion(historial: list[dict], op: Operacion, sk: Soaking, v: Verificacion) -> bool:
    """Agrega una iteración numerada si el resultado cambió respecto de la última.

    Así cada prueba de T1/T2 queda registrada una sola vez, aunque la página se recalcule.
    """
    fila = {"T1 [°C]": op.T1_C, "T2 [°C]": op.T2_C, "cad [s]": round(op.cad_s, 4),
            "Sk [min]": round(sk.sk_min, 4), "Tsk [°C]": round(sk.tsk_C, 3),
            "cumple": "Sí" if v.cumple else "No"}
    if historial and {k: historial[-1][k] for k in fila} == fila:
        return False
    historial.append({"Iteración": len(historial) + 1, **fila})
    return True
