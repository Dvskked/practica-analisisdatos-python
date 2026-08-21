"""Generación de datos sintéticos de ventas minoristas.

Generar datos sintéticos realistas es una habilidad fundamental en ciencia de
datos: permite probar pipelines completos sin depender de datos privados ni
descargar ficheros externos. Este módulo crea un histórico de ventas con
patrones del mundo real:

* **Tendencia**: las ventas crecen linealmente con el tiempo.
* **Estacionalidad anual**: picos en noviembre y diciembre (Black Friday y
  Navidad) y caída en verano.
* **Estacionalidad semanal**: los fines de semana se vende más.
* **Clientes fieles**: unos pocos clientes concentran muchas compras
  (distribución de Pareto), lo que da sentido al análisis RFM posterior.
* **Ruido aleatorio**: variabilidad irreducible, como en cualquier dato real.

Todo es reproducible gracias a ``numpy.random.Generator`` con semilla fija.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from retail_analytics import config

# Factores multiplicativos por día de la semana (lunes=0 ... domingo=6)
_FACTOR_DIA_SEMANA = np.array([1.00, 1.00, 1.00, 1.00, 1.05, 1.35, 1.15])

# Factores multiplicativos por mes: reflejan Black Friday y Navidad
_PESOS_MES = {
    1: 0.90, 2: 0.85, 3: 1.00, 4: 1.00, 5: 1.05, 6: 1.00,
    7: 1.05, 8: 0.95, 9: 1.00, 10: 1.10, 11: 1.35, 12: 1.60,
}


def _pesos_temporales(fechas: pd.DatetimeIndex) -> np.ndarray:
    """Calcula el peso relativo de cada día según estacionalidad y tendencia.

    Combina tres efectos multiplicativos:

    1. Día de la semana (fines de semana más fuertes).
    2. Mes del año (campañas comerciales).
    3. Tendencia lineal de crecimiento a lo largo del período.
    """
    factores_dia = _FACTOR_DIA_SEMANA[fechas.dayofweek.to_numpy()]
    factores_mes = np.array([_PESOS_MES[m] for m in fechas.month])
    tendencia = np.linspace(0.85, 1.15, len(fechas))
    pesos = factores_dia * factores_mes * tendencia
    return pesos / pesos.sum()  # normalizar para usar como probabilidades


def generar_clientes(n_clientes: int, rng: np.random.Generator) -> pd.DataFrame:
    """Genera el maestro de clientes con ciudad, edad y fecha de alta.

    Parámetros
    ----------
    n_clientes:
        Número de clientes únicos a crear.
    rng:
        Generador aleatorio (permite reproducibilidad).
    """
    ids = [f"C-{i:05d}" for i in range(1, n_clientes + 1)]
    return pd.DataFrame(
        {
            "id_cliente": ids,
            "ciudad": rng.choice(config.CIUDADES, size=n_clientes, p=config.PESOS_CIUDADES),
            "edad": np.clip(rng.normal(38, 12, n_clientes), 18, 75).round().astype(int),
            "fecha_alta": pd.Timestamp(config.FECHA_INICIO)
            - pd.to_timedelta(rng.integers(30, 900, n_clientes), unit="D"),
        }
    )


def generar_ventas(
    fecha_inicio: str = config.FECHA_INICIO,
    fecha_fin: str = config.FECHA_FIN,
    n_transacciones: int = config.N_TRANSACCIONES,
    n_clientes: int = config.N_CLIENTES,
    semilla: int = config.RANDOM_SEED,
) -> pd.DataFrame:
    """Genera un DataFrame de transacciones de venta sintéticas y realistas.

    Cada fila representa una transacción con producto, precio, cantidad,
    descuento, total, canal, método de pago, ciudad y satisfacción del cliente.

    Parámetros
    ----------
    fecha_inicio / fecha_fin:
        Rango temporal del histórico (inclusive).
    n_transacciones:
        Número de ventas a simular.
    n_clientes:
        Clientes únicos disponibles.
    semilla:
        Semilla aleatoria; la misma semilla produce exactamente los mismos datos.

    Devuelve
    --------
    pd.DataFrame ordenado cronológicamente con identificador único por venta.
    """
    rng = np.random.default_rng(semilla)

    # --- Fechas con estacionalidad -----------------------------------------
    calendario = pd.date_range(fecha_inicio, fecha_fin, freq="D")
    probabilidades = _pesos_temporales(calendario)
    indices_dia = rng.choice(len(calendario), size=n_transacciones, p=probabilidades)
    horas = rng.integers(9, 22, n_transacciones)
    minutos = rng.choice(np.arange(0, 60, 5), size=n_transacciones)
    fecha = calendario[indices_dia] + pd.to_timedelta(horas, unit="h") + pd.to_timedelta(minutos, unit="m")

    # --- Producto y precio según categoría ---------------------------------
    categorias = rng.choice(list(config.CATALOGO), size=n_transacciones, p=config.PESOS_CATEGORIAS)
    producto = np.empty(n_transacciones, dtype=object)
    precio_unitario = np.empty(n_transacciones)
    for categoria, articulos in config.CATALOGO.items():
        mascara = categorias == categoria
        elegidos = rng.integers(0, len(articulos), size=mascara.sum())
        producto[mascara] = [articulos[i][0] for i in elegidos]
        precio_unitario[mascara] = [articulos[i][1] for i in elegidos]

    # --- Cantidad, descuento y total ----------------------------------------
    cantidad = rng.choice([1, 2, 3, 4, 5], size=n_transacciones, p=[0.45, 0.25, 0.15, 0.10, 0.05])
    hay_descuento = rng.random(n_transacciones) < 0.18
    descuento_pct = np.where(hay_descuento, rng.uniform(0.05, 0.30, n_transacciones).round(2), 0.0)
    total = (precio_unitario * cantidad * (1 - descuento_pct)).round(2)

    # --- Satisfacción: los descuentos elevan ligeramente la nota ------------
    satisfaccion = np.clip(3.9 + 0.9 * descuento_pct + rng.normal(0, 0.55, n_transacciones), 1, 5).round(1)

    # --- Dimensiones comerciales --------------------------------------------
    canal = rng.choice(config.CANALES, size=n_transacciones, p=config.PESOS_CANALES)
    metodo_pago = rng.choice(config.METODOS_PAGO, size=n_transacciones, p=config.PESOS_METODOS_PAGO)
    ciudad = rng.choice(config.CIUDADES, size=n_transacciones, p=config.PESOS_CIUDADES)

    # --- Clientes fieles: pesos tipo Pareto ----------------------------------
    # Una minoría de clientes acumula gran parte de las compras, como en el
    # mundo real (principio de Pareto). Esto hará interesante el RFM.
    pesos_fidelidad = rng.pareto(1.5, size=n_clientes) + 0.2
    pesos_fidelidad /= pesos_fidelidad.sum()
    ids_clientes = [f"C-{i:05d}" for i in range(1, n_clientes + 1)]
    id_cliente = rng.choice(ids_clientes, size=n_transacciones, p=pesos_fidelidad)

    df = pd.DataFrame(
        {
            "fecha": fecha,
            "id_cliente": id_cliente,
            "categoria": categorias,
            "producto": producto,
            "precio_unitario": precio_unitario.round(2),
            "cantidad": cantidad,
            "descuento_pct": descuento_pct,
            "total": total,
            "canal": canal,
            "metodo_pago": metodo_pago,
            "ciudad": ciudad,
            "satisfaccion": satisfaccion,
        }
    ).sort_values("fecha", ignore_index=True)

    df.insert(0, "id_transaccion", [f"TX-{i:06d}" for i in range(1, n_transacciones + 1)])
    return df


def guardar_csv(df: pd.DataFrame, ruta: "Path") -> None:
    """Guarda un DataFrame en CSV con codificación UTF-8 BOM.

    El BOM (``utf-8-sig``) hace que Excel muestre correctamente los acentos
    al abrir el archivo directamente.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
