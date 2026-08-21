"""Limpieza de datos e ingeniería de variables.

Se dice que un analista dedica el 80 % de su tiempo a limpiar datos. Este
módulo implementa las operaciones clásicas:

* Eliminación de **duplicados** por clave primaria.
* Tratamiento de **nulos** (eliminación en claves, imputación con mediana en métricas).
* Detección de **atípicos** mediante el rango intercuartílico (IQR).
* Normalización de texto (espacios y mayúsculas/minúsculas).
* **Ingeniería de variables** temporales: año, mes, trimestre, día de la
  semana, indicador de fin de semana...
"""

from __future__ import annotations

import numpy as np
import pandas as pd

_DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

_COLUMNAS_TEXTO = ["categoria", "producto", "ciudad"]
_COLUMNAS_CLAVE = ["id_transaccion", "fecha", "id_cliente", "producto", "cantidad", "total"]


def resumen_calidad(df: pd.DataFrame) -> pd.DataFrame:
    """Genera un informe de calidad: nulos por columna, duplicados y memoria.

    Devuelve un DataFrame con una fila por columna, ideal para revisar antes
    de limpiar.
    """
    informe = pd.DataFrame(
        {
            "tipo": df.dtypes.astype(str),
            "nulos": df.isna().sum(),
            "pct_nulos": (df.isna().mean() * 100).round(2),
            "unicos": df.nunique(),
        }
    )
    return informe


def mascara_atipicos_iqr(serie: pd.Series, factor: float = 3.0) -> pd.Series:
    """Devuelve una máscara booleana: ``True`` donde el valor es atípico.

    El método IQR considera atípico todo valor fuera del intervalo
    ``[Q1 - factor·IQR, Q3 + factor·IQR]``. Con ``factor=1.5`` la detección es
    agresiva; con ``3.0`` solo se marcan atípicos extremos, criterio habitual
    cuando no queremos descartar ventas grandes legítimas.
    """
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1
    limite_inferior = q1 - factor * iqr
    limite_superior = q3 + factor * iqr
    return (serie < limite_inferior) | (serie > limite_superior)


def limpiar_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el proceso completo de limpieza al dataset de ventas.

    Pasos aplicados, en orden:

    1. Eliminar duplicados por ``id_transaccion``.
    2. Eliminar filas sin datos críticos (claves o importes).
    3. Imputar ``satisfaccion`` faltante con la mediana.
    4. Descartar importes imposibles (negativos o cero unidades).
    5. Normalizar textos (espacios sobrantes).
    6. Marcar atípicos extremos de ``total`` sin eliminarlos (columna booleana).

    Devuelve una copia limpia; el original no se modifica.
    """
    df = df.copy()

    df = df.drop_duplicates(subset="id_transaccion", keep="first")
    df = df.dropna(subset=[c for c in _COLUMNAS_CLAVE if c in df.columns])

    if "satisfaccion" in df.columns:
        mediana_satisfaccion = df["satisfaccion"].median()
        df["satisfaccion"] = df["satisfaccion"].fillna(mediana_satisfaccion)

    if "precio_unitario" in df.columns:
        df = df[df["precio_unitario"] > 0]
    if "cantidad" in df.columns:
        df = df[df["cantidad"] > 0]
    if "total" in df.columns:
        df = df[df["total"] >= 0]

    for columna in _COLUMNAS_TEXTO:
        if columna in df.columns:
            df[columna] = df[columna].astype(str).str.strip()

    if "total" in df.columns:
        df["atipico_total"] = mascara_atipicos_iqr(df["total"]).astype(bool)

    return df.reset_index(drop=True)


def agregar_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece el dataset con variables derivadas de la fecha y del importe.

    Las columnas temporales derivadas son la base de casi cualquier análisis
    de estacionalidad; calcularlas una sola vez evita repetir lógica en cada
    gráfica posterior.
    """
    df = df.copy()
    fecha = df["fecha"]

    df["año"] = fecha.dt.year
    df["mes_num"] = fecha.dt.month
    df["mes"] = df["mes_num"].map(_MESES)
    df["trimestre"] = "T" + fecha.dt.quarter.astype(str)
    df["dia_semana"] = fecha.dt.dayofweek.map(dict(enumerate(_DIAS_SEMANA)))
    df["es_fin_de_semana"] = fecha.dt.dayofweek >= 5
    df["semana_iso"] = fecha.dt.isocalendar().week.astype(int)
    df["importe_medio_unitario"] = (df["total"] / df["cantidad"]).round(2)

    orden_meses = list(_MESES.values())
    df["mes"] = pd.Categorical(df["mes"], categories=orden_meses, ordered=True)
    df["dia_semana"] = pd.Categorical(df["dia_semana"], categories=_DIAS_SEMANA, ordered=True)
    return df
