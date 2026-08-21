"""Capa de visualización: tema global, gráficas estáticas e interactivas."""

from retail_analytics.visualization.interactive_plots import (
    barras_interactivas,
    dispersion_interactiva,
    guardar_html,
    linea_interactiva,
    sunburst_categorias,
)
from retail_analytics.visualization.static_plots import (
    grafico_barras,
    grafico_boxplot_categoria,
    grafico_codo,
    grafico_clusters_2d,
    grafico_descomposicion,
    grafico_dispersion,
    grafico_dia_semana,
    grafico_histograma,
    grafico_mapa_calor,
    grafico_pie,
    grafico_serie_temporal,
    grafico_violin,
)

__all__ = [
    "grafico_histograma",
    "grafico_boxplot_categoria",
    "grafico_mapa_calor",
    "grafico_serie_temporal",
    "grafico_barras",
    "grafico_pie",
    "grafico_dispersion",
    "grafico_violin",
    "grafico_descomposicion",
    "grafico_codo",
    "grafico_clusters_2d",
    "grafico_dia_semana",
    "linea_interactiva",
    "barras_interactivas",
    "sunburst_categorias",
    "dispersion_interactiva",
    "guardar_html",
]
