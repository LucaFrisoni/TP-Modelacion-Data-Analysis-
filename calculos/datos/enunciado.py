"""Datos fijos tomados del enunciado del TP (no dependen del grupo)."""

# Propiedades y geometría del tubo
RHO = 7850.0          # densidad del acero [kg/m3]
OD = 244.48e-3        # diámetro exterior [m]
WT = 13.84e-3         # espesor de pared [m]
LT = 12.0             # longitud del tubo [m]

# Horno
L_HORNO = 50.0        # longitud del horno [m]
N_BOLSILLOS = 50      # cantidad de bolsillos del walking-beam

# Transferencia de calor
HC = 20.0             # coeficiente de convección [W/m2K]
SIGMA = 5.6703e-8     # constante de Stefan-Boltzmann [W/m2K4]
EPSILON = 0.85        # emisividad superficial [-]

# Condición inicial (Ítem 1)
T0_C = 20.0           # [°C]

# Conversión de unidades
KELVIN_OFFSET = 273.15

# Tablas de calor específico: temperatura [°C] -> C [J/kg K]
TEMPERATURAS_TABLA_C = (0.0, 200.0, 300.0, 400.0, 500.0, 600.0, 800.0)
TABLAS_C = {
    "A": (480.0, 520.0, 550.0, 550.0, 550.0, 570.0, 570.0),
    "B": (470.0, 520.0, 540.0, 540.0, 540.0, 560.0, 560.0),
    "C": (480.0, 520.0, 540.0, 540.0, 540.0, 560.0, 560.0),
    "D": (480.0, 530.0, 550.0, 550.0, 550.0, 570.0, 570.0),
}

# Objetivos y tolerancias de calibración (Ítems 3, 4 y 5)
SK_OBJETIVO_MIN = 10.0
TOL_SK_MIN = 1.0
TOL_TSK_C = 2.0
INCREMENTO_PRODUCTIVIDAD = 0.15

# Ancho de la banda de soaking (Ítem 2c): [Tfinal - 10 °C, Tfinal]
ANCHO_BANDA_SOAKING_C = 10.0


def cadencia_s(nref: float) -> float:
    """Cadencia del proceso según la tabla del Ítem 1: 10 s * NREF + 25 s."""
    return 10.0 * nref + 25.0


def temperatura_zona_c(nref: float) -> float:
    """Temperatura de zona del Ítem 1 (T1 = T2): 150 °C * NREF + 550 °C."""
    return 150.0 * nref + 550.0


def tsk_objetivo_caso_c(nref: float, caso: str) -> float:
    """Tsk objetivo de los casos B y C del Ítem 5 (el caso A usa el Tsk del Ítem 3)."""
    bases = {"B": 500.0, "C": 520.0}
    if caso not in bases:
        raise ValueError(f"El caso {caso!r} no tiene Tsk fijo en el enunciado")
    return 150.0 * nref + bases[caso]
