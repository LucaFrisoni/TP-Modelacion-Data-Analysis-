"""Pruebas del cálculo de Sk y Tsk sobre series de temperatura conocidas."""

import numpy as np
import pytest

from calculos.modelo.soaking import calcular_soaking

# Serie sintética con paso de 0,5 min. T final = 700: la banda es [690, 700].
T_MIN = np.arange(8) * 0.5
T_C = np.array([500.0, 650.0, 685.0, 690.0, 694.0, 697.0, 699.0, 700.0])


# Caso base con valores calculables a mano: 5 puntos en banda (690 a 700).
def test_convencion_intervalos_y_tsk_sobre_serie_conocida():
    sk = calcular_soaking(T_MIN, T_C, "intervalos")
    assert sk.sk_min == pytest.approx(4 * 0.5)
    assert sk.tsk_C == pytest.approx(np.mean([690, 694, 697, 699, 700]))
    assert sk.T_final_C == 700.0


# La otra convención cuenta puntos × h: difiere en exactamente un paso.
def test_convencion_puntos_suma_un_paso_mas():
    assert calcular_soaking(T_MIN, T_C, "puntos").sk_min == pytest.approx(5 * 0.5)


# El borde inferior Tfinal - 10 pertenece a la banda (intervalo cerrado [Tfinal - 10, Tfinal]).
def test_punto_en_el_borde_inferior_queda_incluido():
    sk = calcular_soaking(T_MIN, T_C, "intervalos")
    assert sk.en_banda[3] and not sk.en_banda[2]


# "Intervalo acumulado": si la temperatura sale de la banda y vuelve, solo se suman
# los tramos que están dentro.
def test_tiempo_acumulado_ignora_tramos_fuera_de_banda():
    T = np.array([692.0, 695.0, 680.0, 696.0, 698.0, 700.0])
    sk = calcular_soaking(np.arange(6) * 0.5, T, "intervalos")
    assert sk.sk_min == pytest.approx(0.5 + 2 * 0.5)  # tramos (0-1), (3-4) y (4-5)


# Si el tubo se sobrecalienta y se enfría al final, los puntos previos quedan por encima
# de T final y fuera de la banda: Sk colapsa a 0. Este efecto aparece en los Ítems 3 a 5.
def test_sobrecalentamiento_deja_sk_en_cero():
    T = np.array([600.0, 720.0, 715.0, 712.0, 711.0])
    assert calcular_soaking(np.arange(5) * 0.5, T, "intervalos").sk_min == 0.0


# Una convención desconocida debe rechazarse en lugar de devolver un valor arbitrario.
def test_rechaza_convencion_desconocida():
    with pytest.raises(ValueError, match="Convención"):
        calcular_soaking(T_MIN, T_C, "otra")
