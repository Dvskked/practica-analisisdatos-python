"""Segmentación de clientes: análisis RFM + clustering K-Means.

El **análisis RFM** es una técnica clásica de marketing basada en tres
dimensiones del comportamiento de compra:

* **Recencia** (R): días transcurridos desde la última compra.
* **Frecuencia** (F): número de compras realizadas.
* **Valor monetario** (M): gasto total acumulado.

Sobre esas tres variables se aplica **K-Means**, un algoritmo de aprendizaje
no supervisado que agrupa clientes similares en k clústeres. Como K-Means se
basa en distancias euclídeas, las variables deben **estandarizarse** antes
(StandardScaler) para que ninguna domine por su escala.

La elección de k se apoya en dos herramientas:

* **Método del codo**: la inercia (suma de distancias al centroide) cae rápido
  hasta el k "correcto" y luego se aplana; ese quiebro es el k sugerido.
* **Coeficiente de silueta**: mide (−1 a 1) si cada punto está más cerca de su
  propio clúster que de los vecinos; valores > 0.4 indican separación razonable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

NOMBRES_SEGMENTOS = ["Campeones", "Leales", "Potenciales", "En riesgo", "Perdidos"]


def calcular_rfm(df: pd.DataFrame, fecha_referencia: pd.Timestamp | None = None) -> pd.DataFrame:
    """Calcula las métricas RFM por cliente.

    Parámetros
    ----------
    df:
        Dataset de ventas limpio.
    fecha_referencia:
        Fecha contra la que medir la recencia. Por defecto, un día después de
        la última venta del dataset (así ningún cliente tiene recencia negativa).
    """
    if fecha_referencia is None:
        fecha_referencia = df["fecha"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("id_cliente")
        .agg(
            recencia_dias=("fecha", lambda f: (fecha_referencia - f.max()).days),
            frecuencia=("id_transaccion", "count"),
            valor_monetario=("total", "sum"),
        )
        .round(2)
        .reset_index()
    )
    return rfm


def escalar_features(rfm: pd.DataFrame) -> np.ndarray:
    """Estandariza las tres métricas RFM (media 0, desviación típica 1).

    Sin este paso, ``valor_monetario`` (miles de euros) dominaría la distancia
    frente a ``frecuencia`` (unidades pequeñas) y el clustering sería inválido.
    """
    caracteristicas = rfm[["recencia_dias", "frecuencia", "valor_monetario"]]
    return StandardScaler().fit_transform(caracteristicas)


def metodo_codo(
    X: np.ndarray,
    k_min: int = 1,
    k_max: int = 8,
    semilla: int = 42,
) -> list[float]:
    """Calcula la inercia de K-Means para cada k del rango indicado.

    Al representar estas inercias y buscar el "codo" (el punto donde la curva
    deja de caer con fuerza) se obtiene una candidata razonable para k.
    """
    inertias = []
    for k in range(k_min, k_max + 1):
        modelo = KMeans(n_clusters=k, n_init=10, random_state=semilla)
        modelo.fit(X)
        inertias.append(round(float(modelo.inertia_), 1))
    return inertias


def ajustar_kmeans(X: np.ndarray, k: int, semilla: int = 42) -> tuple[np.ndarray, KMeans, float | None]:
    """Entrena K-Means y devuelve etiquetas, modelo y silueta.

    La silueta solo se calcula para k >= 2 (con un único clúster no tiene
    sentido medir separación).
    """
    modelo = KMeans(n_clusters=k, n_init=10, random_state=semilla)
    etiquetas = modelo.fit_predict(X)
    silueta = round(float(silhouette_score(X, etiquetas)), 3) if k >= 2 else None
    return etiquetas, modelo, silueta


def nombrar_segmentos(rfm: pd.DataFrame, etiquetas: np.ndarray) -> dict[int, str]:
    """Asigna nombres de negocio a los clústeres según su valor medio.

    Los clústeres se ordenan por gasto medio descendente y reciben los nombres
    de :data:`NOMBRES_SEGMENTOS` en ese orden: el grupo que más gasta son los
    "Campeones" y el que menos, los "Perdidos".
    """
    gasto_por_cluster = pd.Series(etiquetas).groupby(etiquetas).apply(lambda e: rfm.loc[e.index, "valor_monetario"].mean())
    orden = gasto_por_cluster.sort_values(ascending=False).index.tolist()
    return {cluster: NOMBRES_SEGMENTOS[posicion] for posicion, cluster in enumerate(orden)}


def enriquecer_rfm(rfm: pd.DataFrame, etiquetas: np.ndarray, semilla: int = 42) -> tuple[pd.DataFrame, float | None]:
    """Añade al RFM el número de clúster y su nombre de negocio.

    Devuelve una copia enriquecida junto con la silueta del modelo.
    """
    rfm = rfm.copy()
    _, _, silueta = ajustar_kmeans(escalar_features(rfm), len(np.unique(etiquetas)), semilla)
    mapeo = nombrar_segmentos(rfm, etiquetas)
    rfm["cluster"] = etiquetas
    rfm["segmento"] = rfm["cluster"].map(mapeo)
    return rfm, silueta


def perfil_segmentos(rfm_segmentado: pd.DataFrame) -> pd.DataFrame:
    """Resume el comportamiento medio de cada segmento de clientes.

    La tabla resultante es la que traduce el clustering en acciones de
    marketing: a los "En riesgo" se les lanza una campaña de reactivación, a
    los "Campeones" un programa VIP, etc.
    """
    perfiles = (
        rfm_segmentado.groupby("segmento")
        .agg(
            clientes=("id_cliente", "count"),
            recencia_media_dias=("recencia_dias", "mean"),
            frecuencia_media=("frecuencia", "mean"),
            gasto_medio=("valor_monetario", "mean"),
        )
        .round(1)
        .sort_values("gasto_medio", ascending=False)
        .reset_index()
    )
    total_clientes = perfiles["clientes"].sum()
    perfiles["pct_clientes"] = (perfiles["clientes"] / total_clientes * 100).round(1)
    return perfiles
