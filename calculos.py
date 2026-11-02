"""
Cálculos del proyecto (los usan la app de escritorio y la versión Streamlit).

Variables:
    x = número total de fotos y videos (unidades)
    y = espacio ocupado por la galería (GB)
    z = espacio total usado del almacenamiento interno (GB)

  1. leer_datos():  lee los 20 datos de la encuesta desde datos.csv
  2. ajustar():     calcula las regresiones con numpy (mínimos cuadrados),
                    igual que la línea de tendencia de Excel
        y(x): lineal y cuadrática
        z(y): exponencial y logarítmica
        z(y(x)): la función compuesta de cada combinación
"""
import csv
import sys
from pathlib import Path

import numpy as np

# Carpeta del programa (también funciona si se convierte en .exe con PyInstaller)
CARPETA = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ARCHIVO_DATOS = CARPETA / "datos.csv"


def leer_datos():
    """Devuelve una lista de filas [x, y, z] leídas de datos.csv."""
    filas = []
    with open(ARCHIVO_DATOS, newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            x, y, z = float(fila["x"]), float(fila["y"]), float(fila["z"])
            filas.append([int(x) if x.is_integer() else x, y, z])
    return filas


def r_cuadrado(real, estimado):
    """R² = 1 - (suma de errores al cuadrado) / (variación total)."""
    real, estimado = np.asarray(real, float), np.asarray(estimado, float)
    sse = np.sum((real - estimado) ** 2)
    sst = np.sum((real - real.mean()) ** 2)
    return 1 - sse / sst


def numero(v):
    """Convierte a número normal de Python; si no es válido devuelve None."""
    v = float(v)
    return v if np.isfinite(v) else None


def ajustar(filas):
    x, y, z = (np.array(c, float) for c in zip(*filas))

    # --- y(x): polinómica -------------------------------------------------
    b1, a1 = np.polyfit(x, y, 1)            # y = a + b·x
    c2, c1, c0 = np.polyfit(x, y, 2)        # y = c2·x² + c1·x + c0
    y_lin = a1 + b1 * x
    y_cuad = c2 * x**2 + c1 * x + c0

    # --- z(y): exponencial y logarítmica ----------------------------------
    k, ln_A = np.polyfit(y, np.log(z), 1)   # ln z = ln A + k·y  (recta en ln z)
    A = np.exp(ln_A)
    b2, a2 = np.polyfit(np.log(y), z, 1)    # z = a + b·ln y     (recta en ln y)

    def z_exp(v):
        return A * np.exp(k * v)

    def z_log(v):
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(v > 0, a2 + b2 * np.log(v), np.nan)

    # --- función compuesta z(y(x)) para las 4 combinaciones ---------------
    compuestas = {}
    for nombre_y, valores_y in (("lin", y_lin), ("quad", y_cuad)):
        for nombre_z, f in (("exp", z_exp), ("log", z_log)):
            estimado = f(valores_y)
            ok = np.isfinite(estimado).all()
            compuestas[f"{nombre_y}_{nombre_z}"] = numero(r_cuadrado(z, estimado)) if ok else None

    return {
        "yx": {
            "lin": {"a": numero(a1), "b": numero(b1), "r2": numero(r_cuadrado(y, y_lin))},
            "quad": {"c0": numero(c0), "c1": numero(c1), "c2": numero(c2),
                     "r2": numero(r_cuadrado(y, y_cuad))},
        },
        "zy": {
            # Igual que Excel: el R² del exponencial se calcula sobre ln(z)
            "exp": {"A": numero(A), "k": numero(k),
                    "r2": numero(r_cuadrado(np.log(z), ln_A + k * y)),
                    "r2_real": numero(r_cuadrado(z, z_exp(y)))},
            "log": {"a": numero(a2), "b": numero(b2), "r2": numero(r_cuadrado(z, z_log(y)))},
        },
        "comp": compuestas,
    }
