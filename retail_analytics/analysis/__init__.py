"""Capa de análisis: estadística descriptiva, temporal, correlaciones y segmentación."""

from retail_analytics.analysis.correlation import correlaciones_significativas, matriz_correlacion
from retail_analytics.analysis.descriptive import (
    calcular_kpis,
    estadisticas_ticket,
    imprimir_kpis,
    resumen_por_categoria,
    resumen_por_ciudad,
    top_productos,
)
from retail_analytics.analysis.segmentation import (
    ajustar_kmeans,
    calcular_rfm,
    escalar_features,
    metodo_codo,
    nombrar_segmentos,
    perfil_segmentos,
)
from retail_analytics.analysis.temporal import (
    comparar_canales_por_mes,
    crecimiento_interanual,
    descomposicion_estacional,
    media_movil,
    resumen_dia_semana,
    serie_mensual,
)

__all__ = [
    "calcular_kpis",
    "imprimir_kpis",
    "resumen_por_categoria",
    "resumen_por_ciudad",
    "top_productos",
    "estadisticas_ticket",
    "serie_mensual",
    "media_movil",
    "descomposicion_estacional",
    "crecimiento_interanual",
    "resumen_dia_semana",
    "comparar_canales_por_mes",
    "matriz_correlacion",
    "correlaciones_significativas",
    "calcular_rfm",
    "escalar_features",
    "metodo_codo",
    "ajustar_kmeans",
    "nombrar_segmentos",
    "perfil_segmentos",
]
