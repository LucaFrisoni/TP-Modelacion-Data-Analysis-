"""Configuración de cálculo: datos del grupo + decisiones del equipo, y armado del modelo de cada ítem."""

from dataclasses import dataclass

from calculos.datos import decisiones as D
from calculos.datos import enunciado as E
from calculos.datos import grupo
from calculos.metodos.minimos_cuadrados import AjustePolinomico
from calculos.modelo.calor_especifico import ajuste_tabla, calor_constante, promedio_tabla
from calculos.modelo.modelo_termico import ModeloTermico
from calculos.modelo.parametros import Operacion, operacion_base
from calculos.modelo.soaking import CONVENCIONES_SK


@dataclass(frozen=True)
class Configuracion:
    """NREF y tabla son los del grupo; grado y convención de Sk son decisiones del equipo."""

    grado_c: int = D.GRADO_C
    convencion_sk: str = D.CONVENCION_SK
    nref: float = grupo.NREF
    tabla_c: str = grupo.TABLA_C

    def __post_init__(self):
        if self.tabla_c not in E.TABLAS_C:
            raise ValueError(f"Tabla {self.tabla_c!r} inexistente")
        if not 0 <= self.grado_c < len(E.TEMPERATURAS_TABLA_C):
            raise ValueError(f"Grado {self.grado_c} fuera de rango")
        if self.convencion_sk not in CONVENCIONES_SK:
            raise ValueError(f"Convención de Sk {self.convencion_sk!r} desconocida")

    def operacion_base(self) -> Operacion:
        return operacion_base(self.nref)

    def c_medio(self) -> float:
        return promedio_tabla(self.tabla_c)

    def ajuste_c(self) -> AjustePolinomico:
        return ajuste_tabla(self.tabla_c, self.grado_c)

    def modelo(self, operacion: Operacion, radiacion: bool, c_variable: bool) -> ModeloTermico:
        """Modelo con o sin radiación, con C promedio o con el ajuste C(T) elegido."""
        calor = self.ajuste_c() if c_variable else calor_constante(self.c_medio())
        return ModeloTermico(operacion, calor, radiacion)
