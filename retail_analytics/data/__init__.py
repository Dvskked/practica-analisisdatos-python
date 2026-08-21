"""Capa de datos: generación sintética, carga validada y limpieza."""

from retail_analytics.data.cleaner import agregar_variables, limpiar_ventas, resumen_calidad
from retail_analytics.data.generator import generar_clientes, generar_ventas, guardar_csv
from retail_analytics.data.loader import cargar_csv, validar_columnas

__all__ = [
    "generar_ventas",
    "generar_clientes",
    "guardar_csv",
    "cargar_csv",
    "validar_columnas",
    "limpiar_ventas",
    "agregar_variables",
    "resumen_calidad",
]
