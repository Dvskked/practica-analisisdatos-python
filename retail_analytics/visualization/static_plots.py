"""Gráficas estáticas con Matplotlib y Seaborn.

Cada función sigue el mismo contrato profesional:

1. Recibe datos ya preparados (un DataFrame o una Serie).
2. Construye la figura con títulos, etiquetas y anotaciones explicativas.
3. **Devuelve** la figura (no la guarda ni la muestra): quien llama decide
   si guardarla con :func:`retail_analytics.visualization.style.guardar_figura`,
   mostrarla en un notebook o incrustarla en un informe.

Este desacoplamiento hace las funciones reutilizables y fáciles de testear.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.tsa.seasonal import DecomposeResult

from retail_analytics.analysis.correlation import matriz_correlacion


def grafico_histograma(
    serie: pd.Series,
    bins: int = 50,
    titulo: str = "Distribución",
    etiqueta_x: str = "Valor",
) -> plt.Figure:
    """Histograma con curva de densidad (KDE) superpuesta.

    El KDE permite ver la forma de la distribución sin depender del número de
    barras elegido.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(serie, bins=bins, kde=True, ax=ax, color="#2E86AB", edgecolor="white", alpha=0.85)
    media = serie.mean()
    mediana = serie.median()
    ax.axvline(media, color="#C73E1D", ls="--", lw=1.6, label=f"Media: {media:,.0f}")
    ax.axvline(mediana, color="#F18F01", ls=":", lw=1.8, label=f"Mediana: {mediana:,.0f}")
    ax.set(title=titulo, xlabel=etiqueta_x, ylabel="Frecuencia")
    ax.legend()
    return fig


def grafico_boxplot_categoria(
    df: pd.DataFrame,
    columna_categoria: str,
    columna_valor: str,
    titulo: str | None = None,
) -> plt.Figure:
    """Boxplot de una variable numérica agrupado por categoría.

    Los boxplots muestran mediana, cuartiles y atípicos: perfectos para
    comparar distribuciones entre grupos.
    """
    orden = (
        df.groupby(columna_categoria, observed=True)[columna_valor]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.boxplot(
        data=df,
        x=columna_categoria,
        y=columna_valor,
        order=orden,
        showfliers=False,
        palette="crest",
        hue=columna_categoria,
        legend=False,
        ax=ax,
    )
    ax.set(
        title=titulo or f"Distribución de {columna_valor} por {columna_categoria}",
        xlabel=None,
        ylabel=columna_valor.replace("_", " ").capitalize(),
    )
    ax.tick_params(axis="x", rotation=20)
    return fig


def grafico_mapa_calor(df: pd.DataFrame, columnas: list[str] | None = None) -> plt.Figure:
    """Mapa de calor de la matriz de correlaciones de Pearson.

    Colores cálidos = correlación positiva; fríos = negativa. La anotación
    numérica evita interpretaciones erróneas por tono.
    """
    matriz = matriz_correlacion(df, columnas)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(
        matriz,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.6,
        cbar_kws={"shrink": 0.85},
        ax=ax,
    )
    ax.set_title("Matriz de correlaciones (Pearson)", pad=14)
    ax.tick_params(axis="x", rotation=30)
    return fig


def grafico_serie_temporal(
    serie: pd.Series,
    media_movil: pd.Series | None = None,
    ventana_mm: int = 3,
    titulo: str = "Evolución temporal",
    etiqueta_y: str = "Ingresos (€)",
) -> plt.Figure:
    """Serie temporal con su media móvil superpuesta.

    La línea fina muestra los valores mensuales reales (con ruido); la línea
    gruesa, la tendencia suavizada.
    """
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(serie.index, serie.values, marker="o", ms=4, lw=1.2, alpha=0.75, label="Mensual")
    if media_movil is not None:
        ax.plot(media_movil.index, media_movil.values, lw=2.8, color="#C73E1D", label=f"Media móvil ({ventana_mm} meses)")
    ax.set(title=titulo, xlabel=None, ylabel=etiqueta_y)
    ax.yaxis.set_major_formatter(lambda x, _: f"{x / 1000:,.0f}k")
    ax.legend()
    fig.autofmt_xdate()
    return fig


def grafico_descomposicion(descomposicion: DecomposeResult, titulo: str = "Descomposición estacional") -> plt.Figure:
    """Representa los cuatro componentes de una descomposición estacional.

    De arriba abajo: serie observada, tendencia, estacionalidad y residuo.
    Un residuo sin patrón visible indica que el modelo capturó bien la estructura.
    """
    fig, ejes = plt.subplots(4, 1, figsize=(12, 9), sharex=False)
    componentes = [
        ("Observado", descomposicion.observed),
        ("Tendencia", descomposicion.trend),
        ("Estacionalidad", descomposicion.seasonal),
        ("Residuo", descomposicion.resid),
    ]
    for ax, (nombre, componente) in zip(ejes, componentes):
        ax.plot(componente.index, componente.values, lw=1.4, color="#2E86AB")
        ax.set_ylabel(nombre)
        ax.yaxis.set_major_formatter(lambda x, _: f"{x / 1000:,.0f}k")
    ejes[0].set_title(titulo, pad=12)
    fig.tight_layout()
    return fig


def grafico_barras(serie: pd.Series, titulo: str = "", etiqueta_y: str = "Ingresos (€)") -> plt.Figure:
    """Barras horizontales ordenadas con etiquetas de valor al final."""
    serie_ordenada = serie.sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, max(4, 0.55 * len(serie_ordenada))))
    colores = sns.color_palette("crest", len(serie_ordenada))
    barras = ax.barh(serie_ordenada.index.astype(str), serie_ordenada.values, color=colores, edgecolor="white")
    maximo = serie_ordenada.max()
    for barra in barras:
        ancho = barra.get_width()
        ax.text(ancho + maximo * 0.01, barra.get_y() + barra.get_height() / 2, f"{ancho:,.0f}", va="center", fontsize=9)
    ax.set(title=titulo, xlabel=etiqueta_y, ylabel=None)
    ax.xaxis.set_major_formatter(lambda x, _: f"{x / 1000:,.0f}k")
    ax.margins(x=0.12)
    return fig


def grafico_dia_semana(serie: pd.Series, titulo: str = "Ingresos por día de la semana") -> plt.Figure:
    """Barras verticales para comparar días de la semana (estacionalidad semanal)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    colores = ["#F18F01" if dia in ("Sábado", "Domingo") else "#2E86AB" for dia in serie.index]
    ax.bar(serie.index.astype(str), serie.values, color=colores, edgecolor="white")
    promedio = serie.mean()
    ax.axhline(promedio, color="#C73E1D", ls="--", lw=1.5, label=f"Promedio: {promedio:,.0f} €")
    ax.set(title=titulo, ylabel="Ingresos (€)")
    ax.yaxis.set_major_formatter(lambda x, _: f"{x / 1000:,.0f}k")
    ax.legend()
    ax.tick_params(axis="x", rotation=15)
    return fig


def grafico_pie(conteos: pd.Series, titulo: str = "") -> plt.Figure:
    """Gráfico circular tipo donut para variables categóricas pocas clases."""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        conteos.values,
        labels=conteos.index.astype(str),
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("crest", len(conteos)),
        wedgeprops={"width": 0.45, "edgecolor": "white"},
        pctdistance=0.78,
    )
    ax.set_title(titulo, pad=16)
    return fig


def grafico_dispersion(
    df: pd.DataFrame,
    x: str,
    y: str,
    titulo: str | None = None,
    regresion: bool = True,
) -> plt.Figure:
    """Diagrama de dispersión con recta de ajuste y correlación anotada.

    La recta se estima por mínimos cuadrados (regresión lineal simple); el
    coeficiente r de Pearson se muestra en la esquina para cuantificar la
    fuerza de la relación.
    """
    fig, ax = plt.subplots(figsize=(9, 6))
    if regresion:
        sns.regplot(data=df, x=x, y=y, ax=ax, scatter_kws={"alpha": 0.25, "s": 18}, line_kws={"color": "#C73E1D", "lw": 2})
    else:
        sns.scatterplot(data=df, x=x, y=y, ax=ax, alpha=0.3, s=18)
    r = df[[x, y]].corr().iloc[0, 1]
    ax.annotate(f"r = {r:.3f}", xy=(0.03, 0.94), xycoords="axes fraction", fontsize=12, fontweight="bold", color="#C73E1D")
    ax.set(title=titulo or f"{y} vs {x}", xlabel=x.replace("_", " "), ylabel=y.replace("_", " "))
    return fig


def grafico_violin(
    df: pd.DataFrame,
    columna_categoria: str,
    columna_valor: str,
    titulo: str | None = None,
) -> plt.Figure:
    """Violín: combina el boxplot con una estimación de densidad por grupo."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.violinplot(
        data=df,
        x=columna_categoria,
        y=columna_valor,
        hue=columna_categoria,
        cut=0,
        inner="quartile",
        density_norm="count",
        palette="crest",
        legend=False,
        ax=ax,
    )
    ax.set(
        title=titulo or f"{columna_valor} por {columna_categoria}",
        xlabel=None,
        ylabel=columna_valor.replace("_", " ").capitalize(),
    )
    ax.tick_params(axis="x", rotation=20)
    return fig


def grafico_codo(inertias: list[float], k_elegido: int = 4) -> plt.Figure:
    """Método del codo: inercia de K-Means frente al número de clústeres.

    El punto marcado señala el k elegido; visualmente debe coincidir con la
    zona donde la curva "se dobla".
    """
    ks = list(range(1, len(inertias) + 1))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ks, inertias, marker="o", lw=2, color="#2E86AB")
    ax.axvline(k_elegido, color="#C73E1D", ls="--", lw=1.5, label=f"k elegido = {k_elegido}")
    ax.set(title="Método del codo para elegir k", xlabel="Número de clústeres (k)", ylabel="Inercia (WCSS)")
    ax.set_xticks(ks)
    ax.legend()
    return fig


def grafico_clusters_2d(
    rfm: pd.DataFrame,
    x: str = "recencia_dias",
    y: str = "valor_monetario",
    hue: str = "segmento",
    titulo: str = "Segmentos de clientes (RFM + K-Means)",
) -> plt.Figure:
    """Dispersión de los clústeres sobre dos dimensiones RFM.

    Recencia en el eje X (izquierda = compró hace poco) y gasto total en el Y:
    la esquina superior izquierda concentra a los mejores clientes.
    """
    fig, ax = plt.subplots(figsize=(10, 6.5))
    sns.scatterplot(data=rfm, x=x, y=y, hue=hue, palette="Set2", s=55, alpha=0.85, edgecolor="white", ax=ax)
    ax.set(title=titulo, xlabel="Recencia (días desde última compra)", ylabel="Gasto total (€)")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v / 1000:,.0f}k")
    ax.legend(title="Segmento", loc="upper right")
    return fig
