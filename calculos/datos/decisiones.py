"""Decisiones y resultados que define el equipo. Son los valores por defecto de la app.

Cuando el equipo cierre una decisión, se actualiza acá y la app publicada la toma
al redesplegar. Ver PENDIENTES_EQUIPO.md.
"""

# TODO: APORTE DEL EQUIPO (Ítem 2a)
#   Grado del polinomio de mínimos cuadrados para C(T). Se usa en los Ítems 2a, 3,
#   4 y 5. Desde la app se puede probar otro grado (panel lateral).
#   Valor actual: 3 = valor de ejemplo, no es una elección justificada.
GRADO_C = 3

# TODO: VALIDAR FÓRMULA O CRITERIO (Ítem 2c)
#   Cómo se convierte "intervalo acumulado" en minutos a partir de puntos discretos
#   (ver calculos/modelo/soaking.py):
#     "intervalos": suma de los intervalos [t_i, t_i+1] con ambos extremos en la banda.
#     "puntos":     cantidad de puntos en banda por el paso h.
#   Difieren en un paso (h = cad = 0,475 min con NREF = 0.35).
CONVENCION_SK = "intervalos"

# TODO: VALIDAR FÓRMULA O CRITERIO (Ítem 1b)
#   Escala por defecto del error relativo: "K" o "C". En la app se puede alternar.
ESCALA_ERROR_RELATIVO = "K"

# TODO: APORTE DEL EQUIPO (Ítem 5) — configuración por defecto de los métodos.
#   Paso de diferencias finitas [°C]; valor inicial (T1, T2) como desplazamiento
#   respecto del Tsk objetivo; tolerancias |F1| [°C] y |F2| [min]; máximo de
#   iteraciones; rango admisible de T1 y T2 [°C]; amortiguación del paso.
#   Valores actuales: de ejemplo. Con T1 muy alto el tubo se sobrecalienta y Sk
#   cae a 0, por eso el valor inicial importa mucho.
DELTA_JACOBIANO_C = 5.0
DESPLAZAMIENTO_INICIAL_C = (120.0, 0.0)
TOL_F1_C = 2.0
TOL_F2_MIN = 1.0
MAX_ITERACIONES = 50
RANGO_FISICO_C = (0.0, 1200.0)
AMORTIGUAR_PASO = False

# TODO: INCORPORAR DATOS PROPORCIONADOS POR EL EQUIPO (Ítems 3 y 4)
#   Resultado definitivo de la calibración manual (T1, T2) [°C]. Mientras sea None,
#   la app usa el que el equipo marque en la sesión con "Usar como resultado".
CALIBRACION_ITEM3_C = None
CALIBRACION_ITEM4_C = None
