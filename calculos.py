"""
Cálculos del proyecto (los usan la app de escritorio y la versión Streamlit).

Variables:
    x = número total de fotos y videos almacenados en el celular (unidades)
    y = espacio ocupado por la galería del celular (GB)
    z = espacio total usado del almacenamiento interno del celular (GB)

  1. leer_datos():  lee los 20 datos de la encuesta desde datos.csv
  2. ajustar():     calcula con numpy las dos regresiones por mínimos cuadrados,
                    igual que la línea de tendencia de Excel
        y(x): regresión lineal         y = a + b·x
        z(y): regresión exponencial    z = A·e^(k·y)
     La función compuesta z(y(x)) se arma reemplazando y(x) dentro de z(y):
        z(y(x)) = A·e^(k·(a + b·x))
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


def numero(v):
    """Convierte a número normal de Python; si no es válido devuelve None."""
    v = float(v)
    return v if np.isfinite(v) else None


def ajustar(filas):
    x, y, z = (np.array(c, float) for c in zip(*filas))

    # y(x): regresión lineal           y = a + b·x
    b, a = np.polyfit(x, y, 1)
    # z(y): regresión exponencial      z = A·e^(k·y)
    # Igual que Excel: se toma ln(z) y queda una recta  ln z = ln A + k·y
    k, ln_A = np.polyfit(y, np.log(z), 1)

    return {
        "yx": {"a": numero(a), "b": numero(b)},
        "zy": {"A": numero(np.exp(ln_A)), "k": numero(k)},
    }
