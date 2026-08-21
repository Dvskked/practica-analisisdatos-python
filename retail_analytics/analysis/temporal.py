"""Análisis de series temporales.

Una serie temporal es cualquier métrica indexada por el tiempo. Este módulo
implementa las herramientas básicas para estudiarla:

* **Agregación mensual** con ``resample``.
* **Media móvil**: promedio de los últimos k meses; suaviza el ruido y revela
  la tendencia subyacente.
* **Descomposición estacional** (statsmodels): separa la serie en tendencia +
  estacionalidad + residuo bajo un modelo aditivo.
* **Crecimiento interanual**: comparación contra el mismo mes del año
  anterior, inmune a la estacionalidad.
"""

from __future__ import annotations

import pandas as pd
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose

from retail_analytics.data.cleaner import _DIAS_SEMANA


def serie_diaria(df: pd.DataFrame) -> pd.Series:
    """Ventas totales agregadas por día."""
    return df.set_index("fecha")["total"].resample("D").sum().round(2)


def serie_mensual(df: pd.DataFrame) -> pd.Series:
    """Ventas totales agregadas por mes (índice datetime con frecuencia).

    ``resample("ME")`` agrupa por fin de mes; es la unidad habitual para ver
    tendencias sin el ruido diario.
    """
    return df.set_index("fecha")["total"].resample("ME").sum().round(2)


def media_movil(serie: pd.Series, ventana: int = 3) -> pd.Series:
    """Calcula la media móvil simple de la serie con la ventana indicada.

    Con datos mensuales, una ventana de 3 meses es el estándar para suavizar;
    una de 12 captura la tendencia anual pura.
    """
    return serie.rolling(window=ventana, min_periods=1).mean().round(2)


def descomposicion_estacional(serie: pd.Series, periodo: int = 12) -> DecomposeResult:
    """Descompone la serie en tendencia, estacionalidad y residuo.

    Usa el modelo **aditivo** (``serie = tendencia + estacionalidad + residuo``),
    apropiado cuando la amplitud estacional no crece con el nivel de la serie.
    Requiere al menos dos períodos completos de datos.
    """
    if len(serie.dropna()) < 2 * periodo:
        raise ValueError(
            f"Se necesitan al menos {2 * periodo} observaciones para descomponer "
            f"con período {periodo}; hay {len(serie.dropna())}."
        )
    return seasonal_decompose(serie, model="additive", period=periodo)


def crecimiento_interanual(serie_mensual_ventas: pd.Series) -> pd.Series:
    """Variación porcentual frente al mismo mes del año anterior (%).

    Al comparar siempre contra el mismo mes del año previo se elimina el
    efecto de la estacionalidad: si diciembre siempre es alto, lo relevante
    es si este diciembre supera al anterior.
    """
    return (serie_mensual_ventas.pct_change(12) * 100).round(1)


def resumen_dia_semana(df: pd.DataFrame) -> pd.Series:
    """Ingresos totales por día de la semana, ordenados de lunes a domingo."""
    ingresos = df.groupby("dia_semana", observed=True)["total"].sum()
    return ingresos.reindex(_DIAS_SEMANA).round(2)


def comparar_canales_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla cruzada mes × canal con los ingresos de cada combinación."""
    tabla = df.pivot_table(
        index="mes",
        columns="canal",
        values="total",
        aggfunc="sum",
        observed=True,
    ).round(2)
    return tabla
