"""Sistema de registro (logging) del proyecto.

El logging es la alternativa profesional a los ``print``: permite niveles de
severidad, formato uniforme, salida simultánea a consola y archivo, y se puede
silenciar o redirigir sin tocar el código de negocio.
"""

from __future__ import annotations

import logging
import sys

from retail_analytics.config import LOGS_DIR

FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configurar_logger(
    nombre: str = "retail_analytics",
    nivel: int = logging.INFO,
    a_archivo: bool = True,
) -> logging.Logger:
    """Configura y devuelve un logger con salida a consola y (opcional) archivo.

    Parámetros
    ----------
    nombre:
        Nombre del logger. Reutilizar el mismo nombre devuelve el mismo logger.
    nivel:
        Nivel mínimo de severidad (DEBUG, INFO, WARNING...).
    a_archivo:
        Si es ``True``, también escribe en ``logs/pipeline.log``.
    """
    logger = logging.getLogger(nombre)
    if logger.handlers:  # ya configurado: evitar handlers duplicados
        return logger

    logger.setLevel(nivel)
    formatter = logging.Formatter(FORMATO, datefmt="%Y-%m-%d %H:%M:%S")

    manejador_consola = logging.StreamHandler(sys.stdout)
    manejador_consola.setFormatter(formatter)
    logger.addHandler(manejador_consola)

    if a_archivo:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        manejador_archivo = logging.FileHandler(LOGS_DIR / "pipeline.log", encoding="utf-8")
        manejador_archivo.setFormatter(formatter)
        logger.addHandler(manejador_archivo)

    logger.propagate = False
    return logger
