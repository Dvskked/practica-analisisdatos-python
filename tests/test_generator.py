"""Pruebas del generador de datos sintéticos."""

from __future__ import annotations

import pandas as pd

from retail_analytics.config import COLUMNAS_VENTAS
from retail_analytics.data.generator import generar_clientes, generar_ventas


class TestGenerarVentas:
    def test_columnas_esperadas(self):
        df = generar_ventas(n_transacciones=100, n_clientes=20)
        faltantes = [col for col in COLUMNAS_VENTAS if col not in df.columns]
        assert not faltantes, f"Faltan columnas: {faltantes}"

    def test_totales_positivos(self):
        df = generar_ventas(n_transacciones=200, n_clientes=30)
        assert (df["total"] > 0).all()
        assert (df["precio_unitario"] > 0).all()
        assert (df["cantidad"] >= 1).all()

    def test_fechas_dentro_del_rango(self):
        df = generar_ventas(fecha_inicio="2024-01-01", fecha_fin="2024-12-31", n_transacciones=150, n_clientes=25)
        assert df["fecha"].min() >= pd.Timestamp("2024-01-01")
        assert df["fecha"].max() <= pd.Timestamp("2024-12-31 23:59")

    def test_reproducibilidad_con_semilla(self):
        df1 = generar_ventas(n_transacciones=120, n_clientes=15, semilla=99)
        df2 = generar_ventas(n_transacciones=120, n_clientes=15, semilla=99)
        pd.testing.assert_frame_equal(df1, df2)

    def test_ids_unicos_y_ordenados(self):
        df = generar_ventas(n_transacciones=80, n_clientes=10)
        assert df["id_transaccion"].is_unique
        assert df["fecha"].is_monotonic_increasing

    def test_satisfaccion_en_rango_valido(self):
        df = generar_ventas(n_transacciones=300, n_clientes=40)
        assert df["satisfaccion"].between(1, 5).all()

    def test_descuento_aplicado_correctamente(self):
        df = generar_ventas(n_transacciones=400, n_clientes=50)
        sin_descuento = df["descuento_pct"] == 0
        recalculado = (
            df["precio_unitario"] * df["cantidad"] * (1 - df["descuento_pct"])
        ).round(2)
        assert (recalculado == df["total"]).all()
        assert sin_descuento.sum() > 0  # hay ventas sin descuento


class TestGenerarClientes:
    def test_forma_y_edades(self):
        clientes = generar_clientes(50, __import__("numpy").random.default_rng(1))
        assert len(clientes) == 50
        assert clientes["edad"].between(18, 75).all()
        assert clientes["id_cliente"].is_unique
