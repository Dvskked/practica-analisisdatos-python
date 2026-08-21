"""Pruebas de la segmentación RFM + K-Means."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from retail_analytics.analysis.segmentation import (
    NOMBRES_SEGMENTOS,
    ajustar_kmeans,
    calcular_rfm,
    escalar_features,
    metodo_codo,
    nombrar_segmentos,
    perfil_segmentos,
)
from retail_analytics.data.generator import generar_ventas


@pytest.fixture(scope="module")
def ventas() -> pd.DataFrame:
    return generar_ventas(n_transacciones=2000, n_clientes=150, semilla=11)


@pytest.fixture(scope="module")
def rfm(ventas: pd.DataFrame) -> pd.DataFrame:
    return calcular_rfm(ventas)


class TestRFM:
    def test_columnas_rfm(self, rfm):
        esperadas = {"id_cliente", "recencia_dias", "frecuencia", "valor_monetario"}
        assert esperadas.issubset(rfm.columns)

    def test_valores_validos(self, rfm):
        assert (rfm["recencia_dias"] >= 0).all()
        assert (rfm["frecuencia"] >= 1).all()
        assert (rfm["valor_monetario"] > 0).all()
        assert rfm["id_cliente"].is_unique

    def test_una_fila_por_cliente(self, rfm, ventas):
        assert len(rfm) == ventas["id_cliente"].nunique()


class TestKMeans:
    def test_escalar_features_estandariza(self, rfm):
        X = escalar_features(rfm)
        assert X.shape == (len(rfm), 3)
        np.testing.assert_allclose(X.mean(axis=0), 0, atol=1e-9)
        np.testing.assert_allclose(X.std(axis=0), 1, atol=1e-9)

    def test_metodo_codo_longitud(self, rfm):
        inertias = metodo_codo(escalar_features(rfm), k_min=1, k_max=5)
        assert len(inertias) == 5
        assert inertias[0] >= inertias[-1]  # la inercia decrece con k

    def test_etiquetas_y_silueta(self, rfm):
        X = escalar_features(rfm)
        etiquetas, modelo, silueta = ajustar_kmeans(X, k=4)
        assert len(etiquetas) == len(rfm)
        assert set(np.unique(etiquetas)) == {0, 1, 2, 3}
        assert modelo.cluster_centers_.shape == (4, 3)
        assert silueta is not None and -1 <= silueta <= 1

    def test_nombres_de_segmento_asignados(self, rfm):
        X = escalar_features(rfm)
        etiquetas, _, _ = ajustar_kmeans(X, k=4)
        mapeo = nombrar_segmentos(rfm, etiquetas)
        assert set(mapeo.values()).issubset(set(NOMBRES_SEGMENTOS))
        assert len(mapeo) == 4

    def test_perfil_segmentos(self, rfm):
        X = escalar_features(rfm)
        etiquetas, _, _ = ajustar_kmeans(X, k=4)
        rfm_seg = rfm.copy()
        mapeo = nombrar_segmentos(rfm, etiquetas)
        rfm_seg["segmento"] = etiquetas
        rfm_seg["segmento"] = rfm_seg["segmento"].map(mapeo)
        perfiles = perfil_segmentos(rfm_seg)
        assert perfiles["clientes"].sum() == len(rfm)
        assert "gasto_medio" in perfiles.columns
