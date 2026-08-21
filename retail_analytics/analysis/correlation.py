"""Análisis de correlaciones con pruebas de significancia.

Una correlación mide la fuerza y dirección de la relación lineal entre dos
variables numéricas:

* **Pearson**: sobre los valores brutos; sensible a atípicos y no-linealidad.
* **Spearman**: sobre los rangos; más robusta, capta relaciones monótonas.

Importante: **correlación no implica causalidad**. Y una correlación calculada
con pocos datos puede ser puro azar: por eso se acompaña de un **p-valor**
(la probabilidad de observar una correlación igual o mayor si en realidad no
hubiera relación). Convención habitual: significativo si p < 0.05.
"""

from __future__ import annotations

from itertools import combinations

import pandas as pd
from scipy import stats

from retail_analytics.config import COLUMNAS_NUMERICAS


def matriz_correlacion(
    df: pd.DataFrame,
    columnas: list[str] | None = None,
    metodo: str = "pearson",
) -> pd.DataFrame:
    """Calcula la matriz de correlaciones entre columnas numéricas.

    Parámetros
    ----------
    df:
        Dataset de entrada.
    columnas:
        Columnas a incluir; por defecto las numéricas de negocio definidas en
        la configuración.
    metodo:
        ``"pearson"`` o ``"spearman"``.
    """
    columnas = [c for c in (columnas or COLUMNAS_NUMERICAS) if c in df.columns]
    if len(columnas) < 2:
        raise ValueError("Se necesitan al menos dos columnas numéricas para correlacionar.")
    return df[columnas].corr(method=metodo).round(3)


def correlaciones_significativas(
    df: pd.DataFrame,
    columnas: list[str] | None = None,
    alfa: float = 0.05,
) -> pd.DataFrame:
    """Lista todos los pares de variables con su r, p-valor y significancia.

    Para cada par se ejecuta un contraste de hipótesis sobre el coeficiente de
    Pearson. El resultado es una tabla ordenada por fuerza absoluta del
    coeficiente, lista para exportar o presentar.
    """
    columnas = [c for c in (columnas or COLUMNAS_NUMERICAS) if c in df.columns]
    filas = []
    for var_a, var_b in combinations(columnas, 2):
        par = df[[var_a, var_b]].dropna()
        r, p_valor = stats.pearsonr(par[var_a], par[var_b])
        filas.append(
            {
                "variable_1": var_a,
                "variable_2": var_b,
                "r_pearson": round(float(r), 3),
                "p_valor": float(p_valor),
                "significativo": bool(p_valor < alfa),
            }
        )
    tabla = pd.DataFrame(filas)
    return tabla.reindex(tabla["r_pearson"].abs().sort_values(ascending=False).index).reset_index(drop=True)
