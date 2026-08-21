"""Utilidades genéricas reutilizables en todo el proyecto."""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any

import pandas as pd


def cronometrar(funcion: Callable) -> Callable:
    """Decorador que mide e imprime la duración de una función.

    Ejemplo
    -------
    >>> @cronometrar
    ... def tarea_lenta():
    ...     time.sleep(1)
    """

    @functools.wraps(funcion)
    def envoltorio(*args: Any, **kwargs: Any) -> Any:
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        duracion = time.perf_counter() - inicio
        print(f"⏱  {funcion.__name__} tardó {duracion:.2f} s")
        return resultado

    return envoltorio


def formatear_moneda(valor: float) -> str:
    """Formatea un número como moneda en formato español (1.234,56 €).

    Python formatea por defecto al estilo inglés (1,234.56); este helper lo
    convierte al convenio español intercambiando separadores.
    """
    texto = f"{valor:,.2f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".") + " €"


def resumen_dataframe(df: pd.DataFrame) -> str:
    """Devuelve un resumen textual de un DataFrame: forma, memoria y nulos.

    Útil como primer contacto con cualquier dataset nuevo.
    """
    memoria_mb = df.memory_usage(deep=True).sum() / 1024**2
    nulos_totales = int(df.isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    lineas = [
        f"Dimensiones      : {df.shape[0]:,} filas × {df.shape[1]} columnas",
        f"Memoria          : {memoria_mb:.2f} MB",
        f"Celdas nulas     : {nulos_totales:,}",
        f"Filas duplicadas : {duplicados:,}",
        f"Tipos de dato    : {dict(df.dtypes.value_counts())}",
    ]
    return "\n".join(lineas)
