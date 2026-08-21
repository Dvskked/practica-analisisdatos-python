"""Carga de datos desde CSV con validación de esquema.

Validar el esquema al cargar (columnas presentes, tipos correctos) detecta
errores en la frontera del sistema y no a mitad del análisis: un fallo temprano
y claro vale más que uno tardío y críptico.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from retail_analytics.config import COLUMNAS_VENTAS


def validar_columnas(df: pd.DataFrame, requeridas: list[str]) -> None:
    """Comprueba que el DataFrame contiene todas las columnas requeridas.

    Lanza
    -----
    ValueError
        Si falta alguna columna, indicando cuáles faltan.
    """
    faltantes = [col for col in requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(
            "Faltan columnas obligatorias en el dataset: "
            f"{faltantes}. Columnas encontradas: {list(df.columns)}"
        )


def cargar_csv(
    ruta: Path,
    columna_fecha: str | None = "fecha",
    columnas_requeridas: list[str] | None = None,
) -> pd.DataFrame:
    """Carga un archivo CSV convirtiendo la columna de fecha a datetime.

    Parámetros
    ----------
    ruta:
        Ruta del archivo CSV.
    columna_fecha:
        Nombre de la columna temporal a parsear; ``None`` para no parsear.
    columnas_requeridas:
        Esquema mínimo exigido; por defecto el esquema completo de ventas.

    Devuelve
    --------
    pd.DataFrame validado.
    """
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}\n"
            "Sugerencia: ejecuta antes el generador (scripts/run_pipeline.py)."
        )

    df = pd.read_csv(ruta, encoding="utf-8-sig")

    if columna_fecha is not None and columna_fecha in df.columns:
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])

    validar_columnas(df, columnas_requeridas or COLUMNAS_VENTAS)
    return df
