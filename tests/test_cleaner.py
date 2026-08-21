"""Pruebas del módulo de limpieza de datos."""

from __future__ import annotations

import numpy as np
import pandas as pd

from retail_analytics.data.cleaner import agregar_variables, limpiar_ventas, mascara_atipicos_iqr


def _dataset_sucio() -> pd.DataFrame:
    """Dataset diminuto con errores plantados a propósito."""
    return pd.DataFrame(
        {
            "id_transaccion": ["TX-1", "TX-2", "TX-2", "TX-3", "TX-4"],
            "fecha": pd.to_datetime(
                ["2024-01-05 10:00", "2024-01-06 11:00", "2024-01-06 11:00", "2024-01-07 12:00", "2024-01-08 13:00"]
            ),
            "id_cliente": ["C-1", "C-2", "C-2", None, "C-3"],
            "categoria": [" Ropa ", "Hogar", "Hogar", "Libros", "Ropa"],
            "producto": ["Camisa", "Taza", "Taza", "Novela", "Pantalón"],
            "precio_unitario": [20.0, 5.0, 5.0, 15.0, -30.0],
            "cantidad": [2, 1, 1, 3, 1],
            "descuento_pct": [0.0, 0.10, 0.10, 0.0, 0.0],
            "total": [40.0, 4.50, 4.50, 45.0, -30.0],
            "satisfaccion": [4.0, np.nan, np.nan, 5.0, 3.0],
        }
    )


class TestLimpiarVentas:
    def test_elimina_duplicados(self):
        limpio = limpiar_ventas(_dataset_sucio())
        assert limpio["id_transaccion"].is_unique

    def test_elimina_nulos_en_claves(self):
        limpio = limpiar_ventas(_dataset_sucio())
        assert not limpio["id_cliente"].isna().any()

    def test_imputa_satisfaccion_con_mediana(self):
        limpio = limpiar_ventas(_dataset_sucio())
        assert not limpio["satisfaccion"].isna().any()

    def test_descarta_importes_negativos(self):
        limpio = limpiar_ventas(_dataset_sucio())
        assert (limpio["total"] >= 0).all()
        assert (limpio["precio_unitario"] > 0).all()

    def test_no_modifica_original(self):
        sucio = _dataset_sucio()
        copia_antes = sucio.copy(deep=True)
        limpiar_ventas(sucio)
        pd.testing.assert_frame_equal(sucio, copia_antes)


class TestVariablesDerivadas:
    def test_columnas_temporales_creadas(self):
        df = agregar_variables(limpiar_ventas(_dataset_sucio()))
        esperadas = {"año", "mes_num", "mes", "trimestre", "dia_semana", "es_fin_de_semana", "semana_iso"}
        assert esperadas.issubset(df.columns)

    def test_fin_de_semana_correcto(self):
        df = agregar_variables(limpiar_ventas(_dataset_sucio()))
        # 2024-01-06 y 2024-01-07 son sábado y domingo
        fines = df[df["fecha"].dt.dayofweek >= 5]
        assert (fines["es_fin_de_semana"]).all()

    def test_importe_medio_unitario(self):
        df = agregar_variables(limpiar_ventas(_dataset_sucio()))
        fila = df[df["id_transaccion"] == "TX-1"].iloc[0]
        assert fila["importe_medio_unitario"] == fila["total"] / fila["cantidad"]


class TestAtipicosIQR:
    def test_detecta_valor_extremo(self):
        serie = pd.Series([10, 11, 12, 13, 14, 1000])
        mascara = mascara_atipicos_iqr(serie)
        assert mascara.iloc[-1]
        assert not mascara.iloc[:-1].any()
