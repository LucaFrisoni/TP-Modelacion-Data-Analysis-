# TP Modelación Numérica (CB051): revenido de tubos de acero

**Trabajo práctico:** _"Métodos numéricos aplicados a la ingeniería de procesos"_ · FIUBA · 2.º cuatrimestre 2026 · Curso Martes 14 h

**Integrantes:**

| Integrante                    | Padrón | Carrera                |
| ----------------------------- | ------ | ---------------------- |
| Rocío Menán Iglesias          | 113591 | Ingeniería en Petróleo |
| Julieta Lara Arregui          | 113517 | Ingeniería en Petróleo |
| Marcelo Tomás Cuneo Senmache  | 113790 | Ingeniería en Petróleo |
| Ramiro Besse Molina           | 110657 | Ingeniería en Petróleo |
| Luca Frisoni                  | 113497 | Ingeniería Informática |

**Datos asignados al grupo:** NREF = 0.35 · tabla B de calor específico.

---

## Índice

1. [Propósito y alcance](#1-propósito-y-alcance)
2. [Tecnologías y herramientas](#2-tecnologías-y-herramientas)
3. [Arquitectura del software](#3-arquitectura-del-software)
4. [Funcionalidad y módulos](#4-funcionalidad-y-módulos)
5. [Validación y pruebas](#5-validación-y-pruebas)

---

## 1. Propósito y alcance

El grupo está formado por cuatro estudiantes de Ingeniería en Petróleo y uno de Ingeniería Informática, y el trabajo se dividió según esos perfiles:

- **Análisis físico y matemático** (integrantes de Petróleo): interpretar el modelo térmico, decidir los criterios que deja abiertos la consigna, controlar los resultados y redactar el informe.
- **Herramienta de cálculo** (integrante de Informática): una aplicación web que resuelve los seis ítems y le da al resto del grupo herramientas para analizar los resultados.

La aplicación no reemplaza el análisis: lo facilita. Lo que ofrece:

- Hace todos los cálculos del TP con los datos del grupo: simulación del tubo, ajuste de C(T), soaking, calibraciones y sistema no lineal.
- Muestra gráficos interactivos, que se pueden descargar en PNG de alta resolución para el informe.
- Registra cada prueba de la calibración manual como una iteración numerada.
- Permite descargar cada tabla en CSV (puntos calculados, historiales de iteraciones, resumen) para revisar los números a mano o en Excel.
- Permite cambiar las decisiones que la consigna deja abiertas (grado del polinomio, conteo del soaking, opciones de los métodos del Ítem 5) y ver el efecto al instante.

Aunque está pensada para este TP, el cálculo está separado de la interfaz y los datos están en archivos propios. Cambiando los datos del enunciado o del grupo, la misma herramienta sirve para otro horno, otro tubo u otros objetivos de proceso.

---

## 2. Tecnologías y herramientas

### Lenguaje: Python 3.13

Se eligió Python porque es el lenguaje más usado en cálculo científico y análisis de datos, tiene bibliotecas maduras para todo lo que pide el TP y su código se lee casi como pseudocódigo, lo que facilita que el resto del grupo y la cátedra lo revisen.

### Bibliotecas

| Biblioteca    | Para qué se usa                                                                                                                  |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **NumPy**     | Arreglos numéricos, funciones vectorizadas (`exp`, `mean`, etc.) y resolución de sistemas lineales chicos (`numpy.linalg.solve`). |
| **pandas**    | Tablas de resultados (`DataFrame`) que se muestran en la página y se exportan a CSV.                                            |
| **Plotly**    | Gráficos interactivos (zoom, valores al pasar el mouse, descarga en PNG).                                                       |
| **kaleido**   | Exporta los gráficos de Plotly a PNG para la descarga de todas las figuras. Usa Chromium por detrás.                            |
| **Streamlit** | Framework para hacer la aplicación web escribiendo solo Python (ver [cómo funciona Streamlit](#cómo-funciona-streamlit)).       |
| **pytest**    | Pruebas automáticas (solo en desarrollo).                                                                                       |

**Los métodos numéricos están implementados a mano** (Euler, RK2, mínimos cuadrados, Newton-Raphson, secante y punto fijo). NumPy se usa como herramienta de apoyo (arreglos y sistemas lineales de 2×2 o de 7×7), no para resolver los problemas del TP con funciones ya hechas.

Las versiones están en [requirements.txt](requirements.txt) (lo que necesita la app) y [requirements-dev.txt](requirements-dev.txt) (lo anterior más pytest).

### Docker

Docker es una herramienta de contenedores: empaqueta la aplicación con su versión de Python, sus bibliotecas y Chromium en una imagen que corre igual en cualquier computadora. Se usa en el desarrollo local para que levantar la app sea un solo comando, sin instalar nada a mano:

```bash
docker compose up --build                                   # app en http://localhost:8501
docker compose run --rm app python -m pytest                # correr las pruebas
docker compose run --rm app python generar_resultados.py    # exportar figuras y tablas a resultados/
docker compose down                                         # detener
```

El puerto se define en `.env` (se crea copiando `.env.example`). El código se monta como volumen, así que los cambios se ven al recargar la página.

Sin Docker también funciona: `pip install -r requirements-dev.txt` y después `streamlit run app.py`.

### Otras herramientas

- **Git y GitHub:** control de versiones e historial de cambios.
- **Streamlit Community Cloud:** publica la app en internet a partir del repositorio de GitHub, para que el grupo la use solo con un link.
- **Visual Studio Code:** editor de código.
- **Claude Code (asistente de programación con IA):** se usó para acelerar la escritura del código, las pruebas y la documentación. Las fórmulas, los criterios y los resultados los revisó y validó el grupo (ver la [sección 5](#5-validación-y-pruebas)).

---

## 3. Arquitectura del software

### Idea general

El proyecto está dividido en dos capas que no se mezclan:

- **`calculos/`**: todo el cálculo numérico. No sabe nada de la página web: recibe números y devuelve números, tablas o gráficos. Por eso se puede probar y usar por separado (lo usan las pruebas y el script `generar_resultados.py`).
- **`interfaz/`**: todo lo visual. Pide los resultados a `calculos/` y los muestra en la página.

```
Usuario ──► app.py ──► interfaz/paginas/itemN.py ──► calculos/items/itemN.py ──► calculos/modelo + calculos/metodos
                │                │                                                         │
                │                └──◄── gráficos y tablas ◄── calculos/presentacion ◄──────┘
                └──► interfaz/componentes/panel_lateral.py (tema, decisiones, descargas)
```

### Cómo funciona Streamlit

En Streamlit no se escribe HTML. Cada página es un script de Python que se ejecuta de arriba hacia abajo, y cada llamada como `st.title(...)`, `st.number_input(...)` o `st.plotly_chart(...)` agrega un elemento a la página. Streamlit traduce eso a la página web.

Cada vez que el usuario cambia algo (un número, un botón), Streamlit **vuelve a ejecutar el script** con el valor nuevo. Para que no se pierda lo que se hizo antes (las iteraciones de la calibración manual, las configuraciones guardadas), se usa `st.session_state`, un diccionario que vive mientras dure la sesión del navegador. Por eso, **si se recarga la página, se pierde lo guardado en la sesión** y se vuelve a los valores por defecto.

Solo en algunos lugares puntuales se usa HTML y CSS propio (`st.html`), para detalles de diseño como la tarjeta de integrantes o la animación de carga.

### Orden de ejecución

1. `streamlit run app.py` (o `docker compose up`) levanta el servidor.
2. [app.py](app.py) configura la página, arma el menú de navegación con las 7 páginas, dibuja el panel lateral y ejecuta la página elegida.
3. La página llama a las funciones de `calculos/` y muestra los resultados.

[generar_resultados.py](generar_resultados.py) **no forma parte de la app**: es un script aparte que se corre a mano desde la terminal (ver la [sección 4](#archivos-de-la-raíz)).

### Páginas de la aplicación

| Página           | Qué se ve                                                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Introducción** | Integrantes, consigna en PDF, planteo del problema, modelo térmico, métodos, parámetros del grupo y qué cambia en cada ítem. |
| **Ítem 1**       | Euler explícito, RK2 y solución analítica; error relativo (escala log o lineal, en K o °C); estudio del paso temporal.     |
| **Ítem 2**       | Ajustes de C(T) por mínimos cuadrados (grados 0 a 6); pestañas para 2a (C variable), 2b (radiación) y 2c (soaking).       |
| **Ítem 3**       | Calibración manual de T1 y T2 con indicadores de tolerancia e historial de iteraciones descargable.                       |
| **Ítem 4**       | Nueva cadencia con +15 % de productividad y nueva calibración manual, partiendo del resultado del Ítem 3.                |
| **Ítem 5**       | Newton-Raphson, secante del enunciado y punto fijo para los casos A, B y C; opciones de los métodos; historiales en CSV.  |
| **Ítem 6**       | Tabla resumen con 3 cifras significativas e indicación del origen de cada valor.                                         |

Además, todas las páginas comparten un **panel lateral** con el interruptor de modo claro u oscuro, los datos del grupo, las decisiones que afectan a varios ítems y los botones para descargar todas las figuras (ZIP de PNG) y todas las tablas (ZIP de CSV).

En cuanto a la interfaz de usuario (UI), la navegación es por un menú lateral, cada ítem empieza con un recuadro que explica qué cambia en el planteo, y hay modo claro y oscuro, una animación de carga mientras se calculan los resultados y gráficos con una paleta de colores uniforme.

### Organización de carpetas

```
app.py                       punto de entrada de la app
generar_resultados.py        script que exporta figuras y tablas a resultados/
calculos/                    cálculo numérico, independiente de la interfaz
  datos/                     datos del enunciado, del grupo y decisiones del equipo
  modelo/                    modelo físico del tubo en el horno
  metodos/                   métodos numéricos genéricos
  items/                     cálculo de cada ítem del TP
  presentacion/              gráficos y formato de números
  reporte.py                 arma todas las figuras y tablas y las empaqueta en ZIP
interfaz/                    aplicación web (Streamlit)
  paginas/                   una página por ítem, más la introducción
  componentes/               piezas que usan varias páginas
  recursos/                  estilos CSS, logos de FIUBA y consigna en PDF
tests/                       pruebas automáticas
resultados/                  salida de generar_resultados.py (no se sube al repositorio)
```

- **`calculos/datos/`** tiene tres archivos:
  - [enunciado.py](calculos/datos/enunciado.py): los datos fijos de la consigna (geometría del tubo, horno, coeficientes, tablas de C, objetivos y tolerancias).
  - [grupo.py](calculos/datos/grupo.py): materia, integrantes, NREF y tabla asignada.
  - [decisiones.py](calculos/datos/decisiones.py): lo que decide el equipo y la app usa por defecto (grado del polinomio, conteo del soaking, escala del error, opciones del Ítem 5, calibraciones finales). Cada valor tiene un comentario que explica qué es y en qué ítem se usa.
- **`interfaz/componentes/`** tiene piezas visuales que usan varias páginas: el panel lateral, las descargas, el panel de calibración manual de los Ítems 3 y 4, las opciones del Ítem 5 y el manejo de la sesión. No hacen cálculos: los piden a `calculos/`.
- **`interfaz/recursos/`** cumple el papel de la carpeta `static` de otros frameworks: guarda archivos que no son código (CSS, imágenes y el PDF de la consigna).
- **`__init__.py`:** cada carpeta de código tiene uno. Le indica a Python que la carpeta es un **paquete** y permite importar sus archivos, por ejemplo `from calculos.modelo import parametros`. Cada uno tiene una línea que resume qué hay en esa carpeta.

---

## 4. Funcionalidad y módulos

### Archivos de la raíz

| Archivo                                  | Para qué sirve                                                                                                                                                                                                                                                                 |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `app.py`                                 | Punto de entrada de la app: navegación y panel lateral.                                                                                                                                                                                                                        |
| `generar_resultados.py`                  | Script para la terminal. Calcula todas las figuras (PNG) y tablas (CSV) con los datos de `calculos/datos/` y las guarda en `resultados/`. Sirve para regenerar todo lo del informe de una vez y de forma reproducible. **No** es donde quedan las descargas de la página: esas van a la carpeta de descargas del navegador. |
| `requirements.txt`                       | Bibliotecas y versiones mínimas que necesita la app.                                                                                                                                                                                                                           |
| `requirements-dev.txt`                   | Lo anterior más pytest, para desarrollo.                                                                                                                                                                                                                                       |
| `pytest.ini`                             | Configuración de pytest: busca las pruebas en `tests/` y permite importar `calculos` desde ellas. Va en la raíz porque pytest lo busca desde la carpeta donde se ejecuta.                                                                                                       |
| `packages.txt`                           | Programas del sistema que instala Streamlit Community Cloud al publicar la app. Tiene `chromium`, que kaleido necesita para exportar los gráficos a PNG.                                                                                                                         |
| `Dockerfile`                             | Receta de la imagen de Docker: Python, Chromium y bibliotecas. Tiene una etapa `dev` (con pytest) y una `prod` (solo lo necesario, con un usuario sin privilegios).                                                                                                            |
| `docker-compose.yml`                     | Levanta la imagen `dev` con un solo comando, publica el puerto y monta el código para que los cambios se vean sin reconstruir.                                                                                                                                                  |
| `.env.example`                           | Plantilla de variables de entorno (el puerto). Se copia a `.env`, que no se sube al repositorio.                                                                                                                                                                               |
| `.streamlit/config.toml`                 | Configuración de Streamlit: colores de los temas claro y oscuro, tipografías y opciones del servidor.                                                                                                                                                                         |
| `.gitignore`                             | Lista de archivos que Git no sube al repositorio: entornos virtuales, cachés, `resultados/` y `.env`.                                                                                                                                                                          |
| `.dockerignore`                          | Lo mismo para la imagen de Docker: archivos que no se copian adentro.                                                                                                                                                                                                         |

**`__pycache__/`:** son carpetas que Python crea solo la primera vez que importa un archivo. Guardan el código ya traducido a bytecode (`.pyc`) para que la próxima vez arranque más rápido. No son parte del código fuente; por eso están en `.gitignore`.

### `calculos/modelo/`: el modelo físico

| Archivo y función                                     | Qué hace                                                                                                                                                                                                                  |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[parametros.py](calculos/modelo/parametros.py)**    | Parámetros derivados del enunciado.                                                                                                                                                                                       |
| `Operacion`                                           | Clase inmutable con la condición de operación del horno: cadencia `cad_s` [s], `T1_C` y `T2_C` [°C]. Rechaza cadencias no positivas. `con_temperaturas(T1, T2)` y `con_cadencia(cad)` devuelven una copia con esos valores cambiados (lo usan las calibraciones). |
| `operacion_base(nref)`                                | Operación del Ítem 1 a partir de NREF: cad = 10·NREF + 25 s y T1 = T2 = 150·NREF + 550 °C.                                                                                                                               |
| `masa_kg()`                                           | m = ρ·π·OD·WT·(1 − WT/OD)·Lt, la fórmula del enunciado.                                                                                                                                                                  |
| `superficie_m2()`                                     | S = π·OD·Lt, superficie lateral exterior del tubo.                                                                                                                                                                       |
| `velocidad_m_s(cad)`                                  | v0 = L / (n.° de bolsillos · cad).                                                                                                                                                                                       |
| `tiempo_en_horno_s(cad)`                              | Tiempo que tarda el tubo en recorrer el horno: L / v0 = n.° de bolsillos · cad.                                                                                                                                         |
| `constante_tiempo_conveccion_s(c)`                    | τ = m·C / (hc·S): la escala de tiempo del calentamiento por convección. Se muestra en la introducción.                                                                                                                   |
| `cadencia_por_productividad(cad, incremento)`         | Ítem 4: cad / (1 + incremento). Supone que la productividad (tubos por hora) es proporcional a 1/cad.                                                                                                                    |
| **[calor_especifico.py](calculos/modelo/calor_especifico.py)** | Calor específico C(T). Recibe T en °C porque las tablas están en °C.                                                                                                                                             |
| `tabla(nombre)`                                       | Devuelve las temperaturas y los valores de C de la tabla pedida.                                                                                                                                                         |
| `promedio_tabla(nombre)`                              | C promedio: media de los 7 valores de la tabla (Ítems 1 y 2b).                                                                                                                                                           |
| `calor_constante(c)`                                  | Devuelve una función C(T) que siempre vale `c`.                                                                                                                                                                          |
| `ajuste_tabla(nombre, grado)`                         | C(T) como polinomio de mínimos cuadrados del grado elegido.                                                                                                                                                              |
| `todos_los_ajustes(nombre)`                           | Los ajustes de grado 0 a 6, para comparar en el Ítem 2a.                                                                                                                                                                  |
| **[modelo_termico.py](calculos/modelo/modelo_termico.py)** | La ecuación diferencial: −m·C(T)·dT/dt = hc·S·(T − T∞) + σ·ε·S·(T⁴ − T∞⁴).                                                                                                                                          |
| `ModeloTermico`                                       | Clase que junta una `Operacion`, una función C(T) y si se incluye o no la radiación.                                                                                                                                     |
| `temperatura_entorno_K(t)`                            | T∞ que ve el tubo en el instante t: calcula la posición x = v0·t; si x ≤ L/2 devuelve T1, si no T2.                                                                                                                      |
| `flujo_calor_W(t, T)`                                 | Calor que recibe el tubo: hc·S·(T∞ − T), más σ·ε·S·(T∞⁴ − T⁴) si hay radiación.                                                                                                                                          |
| `derivada(t, T)`                                      | dT/dt = flujo / (m·C(T)). Es la función que se le pasa a Euler o RK2. Si C(T) da negativo, corta con un error.                                                                                                           |
| **[simulacion.py](calculos/modelo/simulacion.py)**    | Resolución de la ecuación a lo largo del horno.                                                                                                                                                                         |
| `Resultado`                                           | Guarda los tiempos [s] y temperaturas [K] calculados; da acceso a minutos, °C y temperatura final.                                                                                                                        |
| `simular(modelo, metodo, subpasos)`                   | Integra desde T0 = 20 °C hasta la salida del horno con paso h = cad / subpasos (1 subpaso = h = cad, como pide el enunciado). Llama a `euler` o `rk2` de `calculos/metodos/integradores.py`.                             |
| `solucion_analitica(op, c, t)`                        | T(t) = T∞ + (T0 − T∞)·e^(−hc·S·t / (m·C)). Solo vale con T1 = T2, sin radiación y con C constante; si no, da error.                                                                                                       |
| `malla_analitica(op, c)`                              | La solución analítica en 400 puntos, para dibujarla como curva continua.                                                                                                                                                 |
| `error_relativo(num, exacta, escala)`                 | \|T_num − T_exacta\| / \|T_exacta\| punto a punto, en K o en °C.                                                                                                                                                         |
| **[soaking.py](calculos/modelo/soaking.py)**          | Parámetros metalúrgicos del Ítem 2c.                                                                                                                                                                                     |
| `Soaking`                                             | Resultado: Sk [min], Tsk [°C], T final y qué puntos quedaron dentro de la banda.                                                                                                                                         |
| `puntos_en_banda(T, ancho)`                           | Marca los puntos con T dentro de [T final − 10 °C, T final].                                                                                                                                                             |
| `tiempo_acumulado_min(t, en_banda, convencion)`       | Convierte esos puntos en minutos. Convención `intervalos`: suma los intervalos con los dos extremos en la banda. Convención `puntos`: cantidad de puntos en banda × h.                                                   |
| `calcular_soaking(t, T, convencion)`                  | Calcula Sk con la convención elegida y Tsk como el promedio de las temperaturas en banda.                                                                                                                                |
| **[unidades.py](calculos/modelo/unidades.py)**        | `c_a_k`, `k_a_c` y `s_a_min`. Los cálculos se hacen en K y s; los resultados se muestran en °C y min.                                                                                                                   |

### `calculos/metodos/`: los métodos numéricos

Son genéricos: no saben nada del horno. Reciben una función y devuelven números, así que se pueden probar con problemas de solución conocida.

| Archivo y función                                          | Qué hace                                                                                                                                                                                                                         |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[integradores.py](calculos/metodos/integradores.py)**    | Métodos para ecuaciones diferenciales, tal como los define el enunciado.                                                                                                                                                         |
| `euler(f, u0, t0, h, n_pasos)`                             | Euler explícito: u(n+1) = u(n) + h·f(t(n), u(n)). Arma con NumPy el vector de tiempos t0, t0 + h, … y llena el vector de temperaturas paso a paso con un `for`. Devuelve los dos vectores.                                         |
| `rk2(f, u0, t0, h, n_pasos)`                               | Runge-Kutta de 2.º orden: q1 = h·f(t(n), u(n)); q2 = h·f(t(n+1), u(n) + q1); u(n+1) = u(n) + (q1 + q2)/2. Misma estructura que `euler`.                                                                                           |
| **[minimos_cuadrados.py](calculos/metodos/minimos_cuadrados.py)** | Ajuste polinómico de C(T).                                                                                                                                                                                                 |
| `ajustar(x, y, grado)`                                     | Arma la matriz de Vandermonde A y resuelve las ecuaciones normales (Aᵀ·A)·a = Aᵀ·y con `numpy.linalg.solve`. Antes lleva T al intervalo [−1, 1] porque, con T hasta 800 y grado 6, la matriz quedaría mal condicionada.        |
| `AjustePolinomico`                                         | Resultado del ajuste: se puede evaluar como una función, da la suma de cuadrados de los residuos, el RMSE y los coeficientes en la variable original (los que van al informe).                                                    |
| `ajustes_hasta_interpolante(x, y)`                         | Todos los ajustes desde grado 0 hasta el interpolante (grado 6 con 7 puntos).                                                                                                                                                    |
| **[sistemas_no_lineales.py](calculos/metodos/sistemas_no_lineales.py)** | Ítem 5: x(k+1) = x(k) − J⁻¹·F(x(k)). Los métodos solo cambian cómo arman J.                                                                                                                                         |
| `Criterio`                                                 | Criterio de parada: tolerancias de \|F1\| y \|F2\|, máximo de iteraciones y rango físico admisible de T1 y T2.                                                                                                                  |
| `iterar(F, x0, fabrica_J, criterio)`                       | Bucle común a todos los métodos. En cada iteración evalúa F, guarda la iteración en el historial, revisa si tiene que parar, pide la J al método, resuelve J·Δx = F y actualiza x.                                               |
| `paso_newton(J, F)`                                        | Resuelve J·Δx = F. Si J es singular o está muy mal condicionada (número de condición > 10¹²), corta con un aviso.                                                                                                                |
| `jacobiano_diferencias(F, x, Fx, delta)`                   | J por diferencias finitas hacia adelante: mueve T1 y después T2 en Δ y mira cuánto cambia F. Cada columna cuesta una simulación.                                                                                                 |
| `jacobiano_secante_enunciado(dx, dF)`                      | J_SEC tal como figura en el enunciado: ΔFi / ΔTj. Sus filas son proporcionales, así que su determinante es siempre 0.                                                                                                            |
| `newton_raphson(F, x0, criterio, delta)`                   | NR: recalcula J por diferencias finitas en cada iteración.                                                                                                                                                                        |
| `secante_enunciado(F, x0, x_previo, criterio)`             | Secante: arma J_SEC con la iteración actual y la anterior.                                                                                                                                                                       |
| `punto_fijo(F, x0, criterio, J)`                           | Punto fijo: J constante (la identidad por defecto, como en el enunciado).                                                                                                                                                        |
| `ResultadoIterativo`                                       | Solución, si convergió, el motivo de parada, el historial de iteraciones y la cantidad de simulaciones usadas.                                                                                                                    |

**Criterio de parada del Ítem 5.** Converge cuando \|F1\| ≤ 2 °C y \|F2\| ≤ 1 min a la vez (tolerancias de la consigna). Se detiene sin converger si llega al máximo de iteraciones, si T1 o T2 salen del rango 0–1200 °C, si F no es finita o si J no se puede invertir.

### `calculos/items/`: el cálculo de cada ítem

Cada archivo junta piezas de `modelo/` y `metodos/` para resolver un ítem.

| Archivo y función                                    | Qué hace                                                                                                                                                                                                                            |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[configuracion.py](calculos/items/configuracion.py)** | Clase inmutable `Configuracion` con lo que define un cálculo: grado del polinomio de C(T), convención de Sk, NREF y tabla. Al crearse verifica que la tabla exista, que el grado esté entre 0 y 6 y que la convención sea válida. |
| `operacion_base()`, `c_medio()`, `ajuste_c()`        | Atajos a la operación del Ítem 1, al C promedio y al ajuste C(T) elegido.                                                                                                                                                          |
| `modelo(op, radiacion, c_variable)`                  | Arma el `ModeloTermico` de cada ítem: con o sin radiación, con C promedio o con C(T).                                                                                                                                              |
| **[item1.py](calculos/items/item1.py)**              |                                                                                                                                                                                                                                     |
| `resolver(cfg)`                                      | Arma el modelo **sin radiación y con C promedio** (`radiacion=False, c_variable=False`) y calcula Euler, RK2 y la solución analítica en los mismos instantes y en una malla fina.                                                    |
| `errores(res, escala)`                               | Error relativo de Euler y RK2 respecto de la analítica.                                                                                                                                                                             |
| `tabla_puntos(res, err)`                             | Tabla con todos los puntos y errores, para verificar a mano.                                                                                                                                                                       |
| `estudio_paso(cfg, escala)`                          | Repite el cálculo con h = cad, cad/2, cad/4 y cad/8. El cociente entre errores consecutivos estima el orden: ≈ 2 para Euler (orden 1) y ≈ 4 para RK2 (orden 2).                                                                     |
| **[item2.py](calculos/items/item2.py)**              |                                                                                                                                                                                                                                     |
| `ajustes`, `tabla_ajustes`, `tabla_coeficientes`     | Todos los ajustes de C(T), su tabla de residuos y los coeficientes del grado elegido.                                                                                                                                              |
| `item2a(cfg)`                                        | RK2 con C(T), sin radiación.                                                                                                                                                                                                        |
| `item2b(cfg)`                                        | RK2 con radiación y C promedio.                                                                                                                                                                                                     |
| `item2c(cfg)`                                        | Sk y Tsk sobre los puntos del 2b.                                                                                                                                                                                                   |
| **[item3.py](calculos/items/item3.py)**              | Lo reutilizan los Ítems 4 y 5.                                                                                                                                                                                                      |
| `evaluar_operacion(cfg, op)`                         | Simula con el **modelo completo** (radiación + C(T)) y calcula Sk y Tsk.                                                                                                                                                            |
| `verificar_objetivo(sk, tsk_obj)`                    | Verifica Sk = 10 ± 1 min y Tsk = objetivo ± 2 °C.                                                                                                                                                                                   |
| `tsk_objetivo(cfg)`                                  | El Tsk objetivo del Ítem 3 es el que da el Ítem 2c.                                                                                                                                                                                 |
| `registrar_iteracion(historial, ...)`                | Agrega una iteración numerada al historial si la combinación T1/T2 cambió.                                                                                                                                                          |
| **[item4.py](calculos/items/item4.py)**              | `cadencia_nueva_s` calcula la cadencia con +15 % de productividad; `operacion_nueva` arma la operación con esa cadencia y las temperaturas que se prueban.                                                                          |
| **[item5.py](calculos/items/item5.py)**              |                                                                                                                                                                                                                                     |
| `OpcionesMetodo`                                     | Opciones editables desde la página: paso Δ de las diferencias finitas, valor inicial (como desplazamiento respecto del Tsk objetivo), tolerancias, máximo de iteraciones, rango físico, J del punto fijo y subpasos. Se puede guardar y cargar en JSON. |
| `objetivos(cfg)`                                     | Tsk objetivo de cada caso: A = Tsk del Ítem 3; B = 150·NREF + 500 °C; C = 150·NREF + 520 °C. En los tres, Sk = 10 min.                                                                                                             |
| `sistema(cfg, tsk_obj)`                              | Arma F(T1, T2) = [Tsk − Tsk_obj, Sk − 10]. Cada evaluación de F es una simulación completa con `evaluar_operacion`.                                                                                                                |
| `resolver(cfg, tsk_obj, metodo, opciones)`           | Elige el método y lo ejecuta desde el valor inicial.                                                                                                                                                                               |
| `tabla_historial`, `tabla_historiales`               | Historial de iteraciones (k, T1, T2, F1, F2) en tablas para mostrar y descargar.                                                                                                                                                  |
| **[item6.py](calculos/items/item6.py)**              | `tabla_resumen` junta los resultados de todos los ítems con 3 cifras significativas e indica el origen de cada valor (modelo, calibración de la sesión, definida por el equipo o método del Ítem 5 con su cantidad de iteraciones). |

### `calculos/presentacion/` y `calculos/reporte.py`

| Archivo y función                                          | Qué hace                                                                                                                                                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **[formato.py](calculos/presentacion/formato.py)**         | `redondear_cifras(x, 3)` redondea a 3 cifras significativas (597.71 → 598; 0.012345 → 0.0123). `texto_cifras` hace lo mismo pero devuelve texto sin notación científica, para la tabla del Ítem 6. |
| **[graficos.py](calculos/presentacion/graficos.py)**       | Arma todas las figuras con Plotly. Cada función recibe resultados y devuelve una figura; no dibuja nada en la página.                                                                           |
| Constantes del inicio                                      | Paleta de colores de las series (y su versión para modo oscuro) y configuración de la barra de Plotly (la cámara descarga PNG en alta resolución).                                              |
| `_estilo(fig, titulo, eje_x, eje_y)`                       | Aplica el mismo estilo a todos los gráficos: título, fondo, grilla, leyenda abajo y tamaño.                                                                                                     |
| `Curva` y `evolucion(curvas, titulo)`                      | Temperatura del tubo en función del tiempo para varias curvas (Ítems 1 y 2).                                                                                                                    |
| `error_relativo(t, errores, escala)`                       | Error relativo de cada método, en escala logarítmica o lineal.                                                                                                                                 |
| `ajustes_calor(T, C, ajustes, grado)`                      | Todos los polinomios de C(T) sobre los puntos de la tabla, resaltando el elegido.                                                                                                              |
| `perfil_horno(op)`                                         | Escalón de temperatura del horno (T1 en la primera mitad, T2 en la segunda) para dibujarlo en línea punteada.                                                                                   |
| `soaking(res, sk, op, titulo)`                             | Evolución del tubo con la banda de soaking sombreada, los puntos en banda, el horno y un recuadro con Sk, Tsk y T final.                                                                        |
| `comparar_operaciones(casos, titulo)`                      | Varias operaciones superpuestas (Ítems 4 y 5), cada una con su horno del mismo color.                                                                                                          |
| `convergencia(historiales, tolerancias)`                   | ‖F / tol‖ por iteración en escala logarítmica. Por debajo de 1 se cumplen las dos tolerancias.                                                                                                  |
| `version_oscura(fig)`                                      | Copia de la figura con los colores del modo oscuro. La original no cambia, así las descargas para el informe salen siempre en modo claro.                                                       |
| **[reporte.py](calculos/reporte.py)**                      | Arma todas las figuras y tablas del TP con una misma configuración (`Entradas`) y las empaqueta en ZIP. Lo usan los botones de descarga del panel lateral y `generar_resultados.py`. Si no hay Chromium para exportar PNG, entrega los gráficos en HTML interactivo. |

### `interfaz/`: la aplicación web

**Páginas** ([interfaz/paginas/](interfaz/paginas/)). Cada archivo es el script de una página. Lee la configuración vigente, llama a las funciones de `calculos/items/` y muestra el resultado con widgets de Streamlit: títulos, recuadros con el planteo, gráficos, métricas, tablas y botones de descarga. Ninguna página hace cuentas: solo piden y muestran.

**Componentes** ([interfaz/componentes/](interfaz/componentes/)):

| Archivo                     | Qué hace                                                                                                                                                                                                              |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `panel_lateral.py`          | Panel lateral: tema, datos del grupo, decisiones del equipo (grado de C(T), conteo de Sk) y descargas.                                                                                                                 |
| `comun.py`                  | Funciones que usan todas las páginas: `configuracion()` (la vigente en la sesión), `grafico()` (muestra una figura con el tema activo), `descarga_csv()`, `planteo()` (recuadro del planteo) y `estado()` (indicador de cumplimiento). |
| `apariencia.py`             | Estilos CSS, logo de FIUBA según el tema, interruptor de modo oscuro y la animación de carga que se ve la primera vez que se abre cada página.                                                                         |
| `calibracion_manual.py`     | Panel de los Ítems 3 y 4: campos para T1 y T2, indicadores de Sk y Tsk con su tolerancia, gráfico, historial de iteraciones y botón "Usar como resultado".                                                             |
| `opciones_item5.py`         | Sección "Opciones del método" del Ítem 5: valor inicial, tolerancias, Δ, máximo de iteraciones, subpasos y J del punto fijo. Permite guardar configuraciones con nombre y descargarlas o importarlas en JSON.           |
| `resultados_sesion.py`      | Guarda en la sesión lo que pasa de un ítem a otro: la calibración elegida en el Ítem 3 (la usa el Ítem 4) y la configuración activa del Ítem 5 (la usan el Ítem 6 y las descargas).                                    |
| `descargas.py`              | Botones "Todas las figuras" y "Todas las tablas" del panel lateral. Los ZIP se generan recién al hacer clic.                                                                                                           |

**Recursos** ([interfaz/recursos/](interfaz/recursos/)): `estilos.css` (estilos propios), logos y emblemas de FIUBA en versión clara y oscura, y `consigna_tp.pdf`, que se descarga desde la introducción.

---

## 5. Validación y pruebas

La validación se hizo de dos formas complementarias.

### Pruebas automáticas

Son programas que ejecutan el código con datos conocidos y verifican el resultado. Se corren con `python -m pytest` y hoy pasan todas. Cada prueba tiene un comentario que explica qué verifica y por qué importa. Están organizadas por módulo:

| Archivo                         | Qué verifica                                                                                                                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_integradores.py`          | Euler y RK2 coinciden con la fórmula cerrada de la ecuación lineal paso a paso, y al dividir h por 2 el error cae ≈ 2 veces (Euler) y ≈ 4 veces (RK2).                                |
| `test_parametros.py`            | Se reproduce el ejemplo del enunciado (NREF = 0.5 → cad = 30 s, T = 625 °C); la masa coincide con el volumen de una corona circular calculado por otro camino; la velocidad es coherente. |
| `test_modelo.py`                | El punto x = L/2 pertenece a la zona 1; C(T) recibe °C; sin diferencia de temperatura no hay intercambio de calor; la radiación acelera el calentamiento.                               |
| `test_simulacion.py`            | RK2 reproduce la solución analítica del Ítem 1; la simulación recorre todo el horno desde 20 °C; con radiación el tubo no supera la temperatura del horno.                               |
| `test_minimos_cuadrados.py`     | El grado 6 pasa por todos los puntos de la tabla; el grado 0 es el promedio; los ajustes coinciden con `numpy.polyfit` (otro algoritmo); el error no aumenta con el grado.             |
| `test_soaking.py`               | Sk y Tsk sobre series calculables a mano, el borde de la banda, tramos que salen y vuelven a la banda, y el sobrecalentamiento que deja Sk en 0.                                        |
| `test_sistemas_no_lineales.py`  | Newton y punto fijo resuelven un sistema con solución conocida; la J_SEC del enunciado es siempre singular; el método se detiene y lo informa al salir del rango físico.                |
| `test_items.py`                 | Con los datos del grupo: el estudio de paso muestra orden 1 y 2; Newton converge en los casos A, B y C, y la solución cumple las tolerancias al volver a simular; formato de 3 cifras.  |
| `test_reporte.py`               | Los ZIP de descarga contienen cada tabla completa; las figuras de los Ítems 3 y 4 aparecen solo con calibración; el modo oscuro no altera las figuras del informe.                     |
| `test_app.py`                   | Cada página se abre sin errores; las iteraciones del Ítem 3 se numeran; el Ítem 4 usa el resultado del Ítem 3; las configuraciones del Ítem 5 se guardan; el modo oscuro funciona.    |

Las pruebas usan **oráculos independientes** siempre que es posible: soluciones analíticas, ejemplos del enunciado, fórmulas calculadas por otro camino o bibliotecas de referencia. Así no se compara el código consigo mismo.

### Verificación manual del grupo

Los integrantes de Ingeniería en Petróleo verificaron a mano algunos cálculos y controlaron que los resultados tuvieran sentido físico. Para eso, las páginas tienen tablas de puntos descargables en CSV ("para verificar a mano o en Excel").

### Lo que las pruebas no validan

Las decisiones académicas que deja abiertas la consigna (grado del polinomio de C(T), convención para contar Sk, escala del error relativo, valor inicial del Ítem 5) las decide y justifica el grupo en el informe. Las pruebas verifican que el código calcula bien con cada opción, no cuál opción es la correcta.

---

**Entrega a la cátedra:** el campus pide que el material de cálculo se llame `software_grupo_xx`. Comprimí esta carpeta con ese nombre al entregar.
