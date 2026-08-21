"""Estadística descriptiva y KPIs de negocio.

La estadística descriptiva resume miles de transacciones en unos pocos
números interpretables. Aquí se calculan los KPIs típicos del retail:

* Facturación total y número de transacciones.
* **Ticket medio** (AOV, *Average Order Value*): ingreso por operación.
* Unidades vendidas, descuento medio y satisfacción media.
* Tablas dinámicas por categoría, producto y ciudad.
"""

from __future__ import annotations

import pandas as pd

from retail_analytics.utils.helpers import formatear_moneda


def calcular_kpis(df: pd.DataFrame) -> dict:
    """Calcula los indicadores clave (KPIs) globales del negocio.

    Devuelve un diccionario con facturación, ticket medio, unidades,
    clientes únicos, descuento medio y satisfacción media, además del
    período cubierto por los datos.
    """
    return {
        "ventas_totales": round(float(df["total"].sum()), 2),
        "n_transacciones": int(len(df)),
        "ticket_promedio": round(float(df["total"].mean()), 2),
        "mediana_ticket": round(float(df["total"].median()), 2),
        "unidades_vendidas": int(df["cantidad"].sum()),
        "clientes_unicos": int(df["id_cliente"].nunique()),
        "productos_distintos": int(df["producto"].nunique()),
        "descuento_medio_pct": round(float(df["descuento_pct"].mean()) * 100, 2),
        "satisfaccion_media": round(float(df["satisfaccion"].mean()), 2),
        "periodo": f"{df['fecha'].min():%d/%m/%Y} — {df['fecha'].max():%d/%m/%Y}",
    }


def imprimir_kpis(kpis: dict) -> str:
    """Convierte el diccionario de KPIs en un bloque de texto legible."""
    lineas = [
        "=" * 46,
        "  INDICADORES CLAVE DEL NEGOCIO (KPIs)",
        "=" * 46,
        f"  Período analizado     : {kpis['periodo']}",
        f"  Ventas totales        : {formatear_moneda(kpis['ventas_totales'])}",
        f"  Nº de transacciones   : {kpis['n_transacciones']:,}",
        f"  Ticket promedio       : {formatear_moneda(kpis['ticket_promedio'])}",
        f"  Mediana del ticket    : {formatear_moneda(kpis['mediana_ticket'])}",
        f"  Unidades vendidas     : {kpis['unidades_vendidas']:,}",
        f"  Clientes únicos       : {kpis['clientes_unicos']:,}",
        f"  Descuento medio       : {kpis['descuento_medio_pct']} %",
        f"  Satisfacción media    : {kpis['satisfaccion_media']} / 5",
        "=" * 46,
    ]
    return "\n".join(lineas)


def resumen_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega ingresos, unidades y satisfacción por categoría de producto.

    Es un ejemplo canónico de ``groupby().agg()``: varias funciones de
    agregación con nombres explícitos para las columnas resultantes.
    """
    resumen = (
        df.groupby("categoria", observed=True)
        .agg(
            transacciones=("id_transaccion", "count"),
            unidades=("cantidad", "sum"),
            ingresos=("total", "sum"),
            ticket_medio=("total", "mean"),
            descuento_medio=("descuento_pct", "mean"),
            satisfaccion_media=("satisfaccion", "mean"),
        )
        .round(2)
        .sort_values("ingresos", ascending=False)
        .reset_index()
    )
    return resumen


def top_productos(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Devuelve los ``n`` productos con más ingresos, con su cuota relativa."""
    ranking = (
        df.groupby(["producto", "categoria"], observed=True)
        .agg(unidades=("cantidad", "sum"), ingresos=("total", "sum"))
        .sort_values("ingresos", ascending=False)
        .head(n)
        .reset_index()
        .round(2)
    )
    total_ingresos = df["total"].sum()
    ranking["cuota_ingresos_pct"] = (ranking["ingresos"] / total_ingresos * 100).round(2)
    return ranking


def resumen_por_ciudad(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega ventas por ciudad ordenadas por ingresos descendentes."""
    return (
        df.groupby("ciudad", observed=True)
        .agg(
            transacciones=("id_transaccion", "count"),
            clientes=("id_cliente", "nunique"),
            ingresos=("total", "sum"),
            ticket_medio=("total", "mean"),
        )
        .round(2)
        .sort_values("ingresos", ascending=False)
        .reset_index()
    )


def estadisticas_ticket(df: pd.DataFrame) -> pd.Series:
    """Estadísticas completas de la distribución del ticket.

    Además del ``describe()`` clásico añade **asimetría** (skewness) y
    **curtosis**: si la asimetría es positiva fuerte, la media del ticket se
    dispara por unas pocas compras muy grandes y conviene mirar la mediana.
    """
    serie = df["total"]
    estadisticas = serie.describe().round(2)
    estadisticas["skewness"] = round(float(serie.skew()), 3)
    estadisticas["kurtosis"] = round(float(serie.kurtosis()), 3)
    return estadisticas
