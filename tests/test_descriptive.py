"""Pruebas de estadística descriptiva, series temporales y correlaciones."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from retail_analytics.analysis.correlation import correlaciones_significativas, matriz_correlacion
from retail_analytics.analysis.descriptive import calcular_kpis, resumen_por_categoria, top_productos
from retail_analytics.analysis.temporal import (
    crecimiento_interanual,
    media_movil,
    serie_mensual,
)
from retail_analytics.data.generator import generar_ventas


@pytest.fixture
def ventas() -> pd.DataFrame:
    return generar_ventas(n_transacciones=1500, n_clientes=120, semilla=7)


class TestKPIs:
    def test_ventas_totales_coincide_con_suma(self, ventas):
        kpis = calcular_kpis(ventas)
        assert kpis["ventas_totales"] == round(float(ventas["total"].sum()), 2)

    def test_kpis_positivos(self, ventas):
        kpis = calcular_kpis(ventas)
        assert kpis["ventas_totales"] > 0
        assert kpis["ticket_promedio"] > 0
        assert kpis["clientes_unicos"] <= 120

    def test_satisfaccion_en_rango(self, ventas):
        assert 1 <= calcular_kpis(ventas)["satisfaccion_media"] <= 5


class TestTablas:
    def test_resumen_categoria_cubre_todas(self, ventas):
        resumen = resumen_por_categoria(ventas)
        assert set(resumen["categoria"]) == set(ventas["categoria"].unique())
        assert (resumen["ingresos"] > 0).all()

    def test_top_productos_limita_y_ordena(self, ventas):
        top = top_productos(ventas, n=5)
        assert len(top) == 5
        assert top["ingresos"].is_monotonic_decreasing


class TestTemporal:
    def test_serie_mensual_frecuencia(self, ventas):
        mensual = serie_mensual(ventas)
        assert isinstance(mensual.index, pd.DatetimeIndex)
        assert (mensual >= 0).all()
        assert len(mensual) >= 20

    def test_media_movil_suaviza(self, ventas):
        mensual = serie_mensual(ventas)
        mm = media_movil(mensual, ventana=3)
        volatilidad_original = mensual.diff().std()
        volatilidad_mm = mm.diff().std()
        assert volatilidad_mm < volatilidad_original

    def test_crecimiento_interanual(self, ventas):
        interanual = crecimiento_interanual(serie_mensual(ventas)).dropna()
        assert not interanual.empty


class TestCorrelacion:
    def test_matriz_simetrica_con_diagonal_uno(self, ventas):
        matriz = matriz_correlacion(ventas)
        assert np.allclose(matriz.values, matriz.values.T)
        assert np.allclose(np.diag(matriz.values), 1.0)

    def test_significancia_precio_total(self, ventas):
        tabla = correlaciones_significativas(ventas)
        par = tabla[
            ((tabla["variable_1"] == "precio_unitario") & (tabla["variable_2"] == "total"))
            | ((tabla["variable_1"] == "total") & (tabla["variable_2"] == "precio_unitario"))
        ]
        assert not par.empty
        # El precio unitario determina el total: la correlación debe ser alta
        assert par.iloc[0]["r_pearson"] > 0.3
