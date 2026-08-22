"""Tema visual global y utilidades de guardado de figuras.

Definir el estilo en un único sitio garantiza que todas las gráficas del
proyecto compartan identidad visual (colores corporativos, tamaños de fuente,
resolución) y que cambiar la "marca" sea una edición de un solo archivo.

Nota técnica: fuera de Jupyter se fuerza el backend no interactivo ``Agg``
para que el código funcione también en servidores y CI sin pantalla.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib

if "JPY_PARENT_PID" not in os.environ:  # solo fuera de notebooks
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from retail_analytics.config import DPI_GUARDADO, FIGURES_DIR, PALETA_COLORES


def aplicar_estilo() -> None:
    """Aplica el tema corporativo del proyecto a Matplotlib y Seaborn."""
    sns.set_theme(style="whitegrid", context="notebook")
    sns.set_palette(PALETA_COLORES)
    plt.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": DPI_GUARDADO,
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "figure.facecolor": "white",
            "axes.facecolor": "#FAFAFA",
            "legend.frameon": True,
        }
    )


# El estilo se aplica al importar el módulo: cualquier gráfica posterior
# hereda automáticamente el tema del proyecto.
aplicar_estilo()


def guardar_figura(fig: plt.Figure, nombre: str, cerrar: bool = True) -> Path:
    """Guarda una figura como PNG de alta resolución en ``reports/figures``.

    Parámetros
    ----------
    fig:
        Figura de Matplotlib a exportar.
    nombre:
        Nombre del archivo (sin extensión).
    cerrar:
        Si es ``True``, cierra la figura tras guardar para liberar memoria;
        desactívalo si necesitas seguir editándola.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    ruta = FIGURES_DIR / f"{nombre}.png"
    fig.savefig(ruta, bbox_inches="tight", facecolor=fig.get_facecolor())
    if cerrar:
        plt.close(fig)
    return ruta
