"""Pipeline principal de análisis de ventas: de los datos crudos al informe.

Ejecuta, en orden y con registro de tiempos:

1. Generación de datos sintéticos  → data/raw/ventas_raw.csv
2. Carga y limpieza                → data/processed/ventas_limpio.csv
3. KPIs de negocio                 → reports/kpis.json (+ consola)
4. Tablas descriptivas             → reports/*.csv
5. Análisis temporal               → figuras PNG + tabla interanual
6. Correlaciones                   → mapa de calor + tabla de significancia
7. Segmentación RFM + K-Means      → CSVs + figuras del codo y clústeres
8. Dashboards interactivos         → reports/figures/*.html

Uso:
    python scripts/run_pipeline.py [--transacciones N] [--clientes N]
                                    [--inicio AAAA-MM-DD] [--fin AAAA-MM-DD]
                                    [--seed N] [--sin-interactivas]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Permitir ejecutar el script directamente sin instalar el paquete:
# se añade la raíz del proyecto al path de búsqueda de módulos.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:  # asegurar salida UTF-8 en consolas Windows antiguas
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

from retail_analytics import config
from retail_analytics.analysis.correlation import correlaciones_significativas
from retail_analytics.analysis.descriptive import (
    calcular_kpis,
    estadisticas_ticket,
    imprimir_kpis,
    resumen_por_categoria,
    resumen_por_ciudad,
    top_productos,
)
from retail_analytics.analysis.segmentation import (
    ajustar_kmeans,
    calcular_rfm,
    escalar_features,
    metodo_codo,
    perfil_segmentos,
)
from retail_analytics.analysis.temporal import (
    comparar_canales_por_mes,
    crecimiento_interanual,
    descomposicion_estacional,
    media_movil,
    resumen_dia_semana,
    serie_mensual,
)
from retail_analytics.data.cleaner import agregar_variables, limpiar_ventas, resumen_calidad
from retail_analytics.data.generator import generar_ventas, guardar_csv
from retail_analytics.data.loader import cargar_csv
from retail_analytics.utils.logger import configurar_logger
from retail_analytics.visualization.interactive_plots import (
    barras_interactivas,
    dispersion_interactiva,
    guardar_html,
    linea_interactiva,
    sunburst_categorias,
)
from retail_analytics.visualization.static_plots import (
    grafico_barras,
    grafico_boxplot_categoria,
    grafico_codo,
    grafico_clusters_2d,
    grafico_descomposicion,
    grafico_dispersion,
    grafico_dia_semana,
    grafico_histograma,
    grafico_mapa_calor,
    grafico_pie,
    grafico_serie_temporal,
)
from retail_analytics.visualization.style import aplicar_estilo, guardar_figura

logger = configurar_logger()
K_CLUSTERS = 4


def paso_generar_datos(args: argparse.Namespace) -> str:
    """Paso 1: genera el dataset sintético y lo guarda como datos crudos."""
    ventas = generar_ventas(
        fecha_inicio=args.inicio,
        fecha_fin=args.fin,
        n_transacciones=args.transacciones,
        n_clientes=args.clientes,
        semilla=args.seed,
    )
    guardar_csv(ventas, config.ARCHIVO_VENTAS_RAW)
    return f"{len(ventas):,} transacciones ({args.inicio} → {args.fin})"


def paso_limpiar_datos() -> object:
    """Paso 2: carga el CSV crudo, limpia y añade variables derivadas."""
    ventas_crudas = cargar_csv(config.ARCHIVO_VENTAS_RAW)
    logger.info("Calidad ANTES de limpiar:\n%s", resumen_calidad(ventas_crudas).to_string())

    ventas_limpias = agregar_variables(limpiar_ventas(ventas_crudas))
    guardar_csv(ventas_limpias, config.ARCHIVO_VENTAS_LIMPIO)

    eliminadas = len(ventas_crudas) - len(ventas_limpias)
    logger.info("Calidad DESPUÉS de limpiar: %s filas (%s eliminadas)", f"{len(ventas_limpias):,}", eliminadas)
    logger.info("Dataset limpio guardado en %s", config.ARCHIVO_VENTAS_LIMPIO)
    return ventas_limpias


def paso_kpis(ventas) -> None:
    """Paso 3: calcula KPIs globales y los exporta a JSON."""
    kpis = calcular_kpis(ventas)
    print("\n" + imprimir_kpis(kpis) + "\n")
    ruta_json = config.REPORTS_DIR / "kpis.json"
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(kpis, archivo, ensure_ascii=False, indent=2)
    logger.info("KPIs exportados a %s", ruta_json)


def paso_tablas_descriptivas(ventas) -> None:
    """Paso 4: exporta tablas por categoría, producto, ciudad y ticket."""
    tablas = {
        "resumen_categoria.csv": resumen_por_categoria(ventas),
        "top_productos.csv": top_productos(ventas),
        "resumen_ciudad.csv": resumen_por_ciudad(ventas),
        "estadisticas_ticket.csv": estadisticas_ticket(ventas).to_frame("valor"),
    }
    for nombre, tabla in tablas.items():
        destino = config.REPORTS_DIR / nombre
        tabla.to_csv(destino, encoding="utf-8-sig")
        logger.info("Tabla exportada: %s", destino)


def paso_analisis_temporal(ventas) -> pd.DataFrame:
    """Paso 5: series mensuales, media móvil, descomposición e interanual."""
    mensual = serie_mensual(ventas)
    mm3 = media_movil(mensual, ventana=3)

    guardar_figura(
        grafico_serie_temporal(mensual, mm3, titulo="Ventas mensuales y tendencia (media móvil 3 meses)"),
        "serie_mensual_media_movil",
    )

    descomposicion = descomposicion_estacional(mensual, periodo=12)
    guardar_figura(grafico_descomposicion(descomposicion), "descomposicion_estacional")

    guardar_figura(grafico_dia_semana(resumen_dia_semana(ventas)), "ingresos_dia_semana")
    guardar_figura(grafico_barras(comparar_canales_por_mes(ventas).sum(), titulo="Ingresos totales por canal"), "ingresos_canal")

    interanual = crecimiento_interanual(mensual).dropna()
    interanual.to_csv(config.REPORTS_DIR / "crecimiento_interanual.csv", encoding="utf-8-sig", header=["crecimiento_pct"])
    if not interanual.empty:
        mejor_mes = interanual.idxmax()
        logger.info(
            "Mejor mes interanual: %s con %+.1f %% de crecimiento",
            mejor_mes.strftime("%m/%Y"),
            interanual.max(),
        )
    return interanual


def paso_correlaciones(ventas) -> None:
    """Paso 6: matriz de correlaciones y contraste de significancia."""
    guardar_figura(grafico_mapa_calor(ventas), "mapa_correlaciones")

    significativas = correlaciones_significativas(ventas)
    significativas.to_csv(config.REPORTS_DIR / "correlaciones_significativas.csv", index=False, encoding="utf-8-sig")
    for _, fila in significativas.head(3).iterrows():
        estado = "significativa" if fila["significativo"] else "NO significativa"
        logger.info(
            "%s ↔ %s: r=%+.3f (p=%.4g) → %s",
            fila["variable_1"],
            fila["variable_2"],
            fila["r_pearson"],
            fila["p_valor"],
            estado,
        )


def paso_segmentacion(ventas) -> tuple[object, float | None]:
    """Paso 7: RFM + K-Means con método del codo y perfiles de segmento."""
    rfm = calcular_rfm(ventas)
    X = escalar_features(rfm)

    inertias = metodo_codo(X, k_min=1, k_max=8, semilla=config.RANDOM_SEED)
    guardar_figura(grafico_codo(inertias, k_elegido=K_CLUSTERS), "metodo_del_codo")

    etiquetas, modelo, silueta = ajustar_kmeans(X, K_CLUSTERS, semilla=config.RANDOM_SEED)
    logger.info("K-Means (k=%s): inercia=%.0f | silueta=%s", K_CLUSTERS, modelo.inertia_, silueta)

    rfm["cluster"] = etiquetas
    from retail_analytics.analysis.segmentation import nombrar_segmentos

    mapeo = nombrar_segmentos(rfm, etiquetas)
    rfm["segmento"] = rfm["cluster"].map(mapeo)

    rfm.to_csv(config.REPORTS_DIR / "rfm_segmentos.csv", index=False, encoding="utf-8-sig")
    perfiles = perfil_segmentos(rfm)
    perfiles.to_csv(config.REPORTS_DIR / "perfiles_segmentos.csv", index=False, encoding="utf-8-sig")
    logger.info("Perfiles de segmento:\n%s", perfiles.to_string(index=False))

    guardar_figura(grafico_clusters_2d(rfm), "segmentos_clientes")
    return rfm, silueta


def paso_interactivas(ventas) -> None:
    """Paso 8: dashboards HTML con Plotly."""
    guardar_html(linea_interactiva(serie_mensual(ventas), titulo="Ventas mensuales interactivas"), "interactivo_serie_mensual")
    guardar_html(sunburst_categorias(ventas, ["canal", "categoria"], titulo="Ingresos: canal → categoría"), "interactivo_sunburst")

    muestra = ventas.sample(n=min(2500, len(ventas)), random_state=config.RANDOM_SEED)
    guardar_html(
        dispersion_interactiva(
            muestra,
            x="total",
            y="satisfaccion",
            color="categoria",
            hover_data=["producto", "ciudad"],
            titulo="Ticket vs satisfacción (muestra aleatoria)",
        ),
        "interactivo_dispersion",
    )
    guardar_html(barras_interactivas(resumen_dia_semana(ventas), titulo="Ingresos por día de la semana"), "interactivo_dia_semana")


def listar_artefactos() -> list[str]:
    """Recopila los archivos generados con su tamaño para el resumen final."""
    lineas = []
    for carpeta in (config.DATA_RAW_DIR, config.DATA_PROCESSED_DIR, config.REPORTS_DIR, config.FIGURES_DIR):
        for archivo in sorted(carpeta.glob("*")):
            if archivo.is_file():
                tamano_kb = archivo.stat().st_size / 1024
                relativo = archivo.relative_to(config.PROJECT_ROOT)
                lineas.append(f"   {str(relativo):<55} {tamano_kb:>9.1f} KB")
    return lineas


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline de análisis de ventas minoristas.")
    parser.add_argument("--transacciones", type=int, default=config.N_TRANSACCIONES)
    parser.add_argument("--clientes", type=int, default=config.N_CLIENTES)
    parser.add_argument("--inicio", type=str, default=config.FECHA_INICIO)
    parser.add_argument("--fin", type=str, default=config.FECHA_FIN)
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED)
    parser.add_argument("--sin-interactivas", action="store_true", help="Omite las gráficas Plotly HTML")
    args = parser.parse_args()

    config.asegurar_directorios()
    aplicar_estilo()

    inicio_total = time.perf_counter()
    pasos: list[tuple[str, float]] = []

    def ejecutar(nombre: str, funcion, *argumentos):
        logger.info("=" * 70)
        logger.info("%s", nombre.upper())
        logger.info("=" * 70)
        t0 = time.perf_counter()
        resultado = funcion(*argumentos) if argumentos else funcion()
        pasos.append((nombre, time.perf_counter() - t0))
        return resultado

    logger.info("RETAIL ANALYTICS — pipeline completo (semilla=%s)", args.seed)

    ejecutar("Paso 1 · Generación de datos sintéticos", paso_generar_datos, args)
    ventas = ejecutar("Paso 2 · Carga y limpieza de datos", paso_limpiar_datos)
    ejecutar("Paso 3 · KPIs de negocio", paso_kpis, ventas)
    ejecutar("Paso 4 · Tablas descriptivas", paso_tablas_descriptivas, ventas)
    ejecutar("Paso 5 · Análisis temporal", paso_analisis_temporal, ventas)
    ejecutar("Paso 6 · Correlaciones", paso_correlaciones, ventas)
    ejecutar("Paso 7 · Segmentación RFM + K-Means", paso_segmentacion, ventas)
    if not args.sin_interactivas:
        ejecutar("Paso 8 · Dashboards interactivos", paso_interactivas, ventas)

    duracion_total = time.perf_counter() - inicio_total
    logger.info("=" * 70)
    logger.info("RESUMEN DE EJECUCIÓN")
    logger.info("=" * 70)
    for nombre, segundos in pasos:
        logger.info("  %-45s %6.2f s", nombre, segundos)
    logger.info("  %-45s %6.2f s", "TOTAL", duracion_total)

    print("\n📁 Archivos generados:")
    for linea in listar_artefactos():
        print(linea)
    print(f"\n✅ Pipeline completado en {duracion_total:.1f} segundos. ¡Feliz análisis!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
