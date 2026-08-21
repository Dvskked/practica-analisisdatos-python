"""Configuración central del proyecto.

Centralizar rutas, semillas y parámetros en un único módulo es una buena
práctica profesional: evita los "números mágicos" dispersos por el código,
facilita el mantenimiento y hace que el comportamiento sea reproducible.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
LOGS_DIR = PROJECT_ROOT / "logs"

ARCHIVO_VENTAS_RAW = DATA_RAW_DIR / "ventas_raw.csv"
ARCHIVO_VENTAS_LIMPIO = DATA_PROCESSED_DIR / "ventas_limpio.csv"

# ---------------------------------------------------------------------------
# Parámetros de generación de datos
# ---------------------------------------------------------------------------
RANDOM_SEED: int = 42
FECHA_INICIO: str = "2024-01-01"
FECHA_FIN: str = "2025-12-31"
N_TRANSACCIONES: int = 12_000
N_CLIENTES: int = 1_500

# Catálogo de productos: categoría -> lista de (producto, precio_base_en_euros)
CATALOGO: dict[str, list[tuple[str, float]]] = {
    "Electrónica": [
        ("Smartphone Galaxy X", 699.0),
        ("Portátil UltraBook 15", 1099.0),
        ("Auriculares Inalámbricos", 129.0),
        ('Monitor 4K 27"', 249.0),
        ("Tablet Pro 11", 449.0),
        ("Smartwatch Active", 199.0),
    ],
    "Hogar": [
        ("Cafetera Espresso", 189.0),
        ("Robot Aspirador", 299.0),
        ("Set Sartenes Antiadherentes", 79.0),
        ("Lámpara Inteligente", 45.0),
        ("Purificador de Aire", 159.0),
    ],
    "Ropa": [
        ("Chaqueta Impermeable", 89.0),
        ("Sudadera Premium", 49.0),
        ("Zapatillas Running", 99.0),
        ("Camisa Clásica", 35.0),
        ("Vaqueros Slim", 59.0),
    ],
    "Deportes": [
        ("Mancuernas Ajustables", 149.0),
        ("Esterilla Yoga Pro", 29.0),
        ("Bicicleta Estática", 349.0),
        ("Set Bandas Elásticas", 19.0),
        ("Balón Profesional", 39.0),
    ],
    "Libros": [
        ("Novela Bestseller", 21.0),
        ("Manual de Python", 39.0),
        ("Biografía Histórica", 25.0),
        ("Libro de Cocina", 28.0),
    ],
    "Alimentación": [
        ("Café en Grano 1kg", 14.0),
        ("Chocolate Artesanal", 6.0),
        ("Aceite de Oliva Extra", 12.0),
        ("Té Verde Premium", 9.0),
        ("Miel Orgánica", 8.0),
    ],
}

PESOS_CATEGORIAS: list[float] = [0.26, 0.20, 0.20, 0.12, 0.08, 0.14]

CIUDADES: list[str] = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga", "Zaragoza"]
PESOS_CIUDADES: list[float] = [0.30, 0.22, 0.14, 0.12, 0.10, 0.07, 0.05]

CANALES: list[str] = ["Online", "Tienda física"]
PESOS_CANALES: list[float] = [0.58, 0.42]

METODOS_PAGO: list[str] = ["Tarjeta", "PayPal", "Efectivo", "Bizum"]
PESOS_METODOS_PAGO: list[float] = [0.52, 0.20, 0.16, 0.12]

# Columnas numéricas usadas en el análisis de correlaciones
COLUMNAS_NUMERICAS: list[str] = [
    "precio_unitario",
    "cantidad",
    "descuento_pct",
    "total",
    "satisfaccion",
]

# Esquema esperado del dataset de ventas (validación al cargar)
COLUMNAS_VENTAS: list[str] = [
    "id_transaccion",
    "fecha",
    "id_cliente",
    "categoria",
    "producto",
    "precio_unitario",
    "cantidad",
    "descuento_pct",
    "total",
    "canal",
    "metodo_pago",
    "ciudad",
    "satisfaccion",
]

# ---------------------------------------------------------------------------
# Estilo de gráficas
# ---------------------------------------------------------------------------
PALETA_COLORES: list[str] = ["#2E86AB", "#F18F01", "#C73E1D", "#3B8686", "#6B5B95", "#A23B72"]
DPI_GUARDADO: int = 150


def asegurar_directorios() -> None:
    """Crea todos los directorios de salida del proyecto si aún no existen."""
    for directorio in (DATA_RAW_DIR, DATA_PROCESSED_DIR, FIGURES_DIR, LOGS_DIR):
        directorio.mkdir(parents=True, exist_ok=True)
