"""Gráficas interactivas con Plotly exportadas como HTML autónomo.

A diferencia de las estáticas, estas gráficas permiten zoom, filtros y
 tooltips al pasar el ratón: ideales para explorar o compartir con perfiles no
 técnicos. Se guardan como ``.html`` que funciona en cualquier navegador.

Se usa ``include_plotlyjs="cdn"`` para archivos ligeros (requieren internet
para renderizar; usa ``True`` si necesitas que funcionen sin conexión).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio

from retail_analytics.config import FIGURES_DIR

pio.templates.default = "plotly_white"


def linea_interactiva(serie: pd.Series, titulo: str = "Evolución temporal", etiqueta_y: str = "Ingresos (€)") -> "px.Figure":
    """Serie temporal interactiva con tooltip unificado al recorrer el eje X."""
    fig = px.line(
        x=serie.index,
        y=serie.values,
        labels={"x": "Fecha", "y": etiqueta_y},
        title=titulo,
        markers=True,
    )
    fig.update_traces(line_color="#2E86AB")
    fig.update_layout(hovermode="x unified", title_font_size=18)
    return fig


def barras_interactivas(serie: pd.Series, titulo: str = "", etiqueta_y: str = "Ingresos (€)") -> "px.Figure":
    """Barras horizontales interactivas ordenadas por valor."""
    serie_ordenada = serie.sort_values()
    fig = px.bar(
        x=serie_ordenada.values,
        y=serie_ordenada.index.astype(str),
        orientation="h",
        labels={"x": etiqueta_y, "y": ""},
        title=titulo,
        text_auto=",.0f",
    )
    fig.update_traces(marker_color="#F18F01")
    fig.update_layout(title_font_size=18)
    return fig


def sunburst_categorias(df: pd.DataFrame, ruta: list[str], valores: str = "total", titulo: str = "") -> "px.Figure":
    """Sunburst jerárquico: anillos concéntricos por niveles de la ruta.

    Perfecto para mostrar cómo se reparten los ingresos en dos niveles, p. ej.
    canal → categoría.
    """
    fig = px.sunburst(df, path=ruta, values=valores, title=titulo or f"Jerarquía {' → '.join(ruta)}")
    fig.update_layout(title_font_size=18)
    return fig


def dispersion_interactiva(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    tamaño: str | None = None,
    hover_data: list[str] | None = None,
    titulo: str = "",
) -> "px.Figure":
    """Nube de puntos interactiva con coloreado por categoría y zoom."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=tamaño,
        hover_data=hover_data,
        title=titulo or f"{y} vs {x}",
        opacity=0.65,
        labels={x: x.replace("_", " "), y: y.replace("_", " ")},
    )
    fig.update_layout(title_font_size=18)
    return fig


def guardar_html(fig: "px.Figure", nombre: str) -> Path:
    """Exporta una figura Plotly a HTML autónomo en ``reports/figures``."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    ruta = FIGURES_DIR / f"{nombre}.html"
    fig.write_html(ruta, include_plotlyjs="cdn")
    return ruta
