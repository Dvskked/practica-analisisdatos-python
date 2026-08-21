# 📊 Retail Analytics — Proyecto Educativo de Análisis de Datos

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/Licencia-MIT-green)
![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![Code style](https://img.shields.io/badge/C%C3%B3digo-PEP%208-black)

> Un pipeline **completo y funcional** de ciencia de datos sobre ventas minoristas:
> generación de datos sintéticos realistas → limpieza → análisis estadístico →
> visualización estática e interactiva → segmentación de clientes con *Machine Learning*.

---

## 📑 Tabla de contenidos

1. [Descripción general](#-descripción-general)
2. [Características](#-características)
3. [Estructura del proyecto](#-estructura-del-proyecto)
4. [Requisitos previos](#-requisitos-previos)
5. [Instalación](#-instalación)
6. [Uso rápido](#-uso-rápido)
7. [Módulos documentados](#-módulos-documentados)
8. [Conceptos educativos que aprenderás](#-conceptos-educativos-que-aprenderás)
9. [Los datos sintéticos](#-los-datos-sintéticos)
10. [Pruebas automatizadas](#-pruebas-automatizadas)
11. [Buenas prácticas aplicadas](#-buenas-prácticas-aplicadas)
12. [Roadmap](#-roadmap)
13. [Contribuir](#-contribuir)
14. [Licencia](#-licencia)
15. [Recursos recomendados](#-recursos-recomendados)

---

## 🔍 Descripción general

Este proyecto simula el flujo de trabajo de un **analista de datos profesional**
en una cadena de tiendas minoristas (*retail*). A partir de un histórico
sintético de ~12 000 transacciones a lo largo de dos años, el pipeline responde
preguntas de negocio reales:

| Pregunta de negocio | Módulo que la resuelve |
|---|---|
| ¿Cuánto facturamos y cuál es el ticket medio? | `analysis/descriptive.py` |
| ¿Cómo evolucionan las ventas mes a mes? ¿Hay estacionalidad? | `analysis/temporal.py` |
| ¿Qué variables se relacionan entre sí y con qué fuerza? | `analysis/correlation.py` |
| ¿Qué tipos de clientes tenemos y cómo fidelizarlos? | `analysis/segmentation.py` |

Todo se orquesta desde un único comando y produce **informes en CSV, gráficas
PNG de alta resolución y dashboards HTML interactivos**.

---

## ✨ Características

- 🧪 **Datos sintéticos realistas**: tendencia de crecimiento, estacionalidad
  anual (Black Friday / Navidad) y semanal (fines de semana), clientes fieles
  con distribución tipo Pareto y ruido aleatorio reproducible (semilla fija).
- 🧹 **Limpieza y calidad de datos**: detección de duplicados/nulos, tratamiento
  de atípicos por rango intercuartílico (IQR) e ingeniería de variables temporales.
- 📈 **Estadística descriptiva**: KPIs de negocio, tablas dinámicas por categoría,
  ciudad, producto y canal; asimetría y curtosis del ticket.
- 📅 **Series temporales**: agregación mensual, medias móviles, descomposición
  estacional (tendencia + estacionalidad + residuo) y crecimiento interanual.
- 🔗 **Correlaciones**: matrices Pearson/Spearman con mapa de calor y pruebas de
  significancia estadística (p-valor).
- 🤖 **Machine Learning no supervisado**: análisis RFM + clustering K-Means con
  método del codo, coeficiente de silueta y perfiles de segmento nombrados.
- 🎨 **Visualización doble**: 11 gráficas estáticas (Matplotlib/Seaborn) y
  dashboards interactivos (Plotly) listos para compartir.
- 🗂️ **Arquitectura modular**: paquete instalable, configuración centralizada,
  logging a archivo y consola, y suite de tests con pytest.
- 📓 **Notebook educativo**: recorrido guiado paso a paso en Jupyter.

---

## 🗂️ Estructura del proyecto

```text
proyecto-analisis-datos/
├── README.md                  ← Estás aquí
├── LICENSE                    ← Licencia MIT
├── pyproject.toml             ← Metadatos y dependencias del paquete
├── requirements.txt           ← Dependencias de ejecución
├── requirements-dev.txt       ← Dependencias de desarrollo (tests, linting)
├── .gitignore
│
├── retail_analytics/          ← 📦 Paquete principal
│   ├── __init__.py
│   ├── config.py              ← Rutas, semillas, catálogo de productos, paleta
│   │
│   ├── data/                  ← Capa de datos
│   │   ├── generator.py       ← Generador de datos sintéticos
│   │   ├── loader.py          ← Carga y validación de CSV
│   │   └── cleaner.py         ← Limpieza + ingeniería de variables
│   │
│   ├── analysis/              ← Capa de análisis
│   │   ├── descriptive.py     ← KPIs y estadística descriptiva
│   │   ├── temporal.py        ← Series temporales y estacionalidad
│   │   ├── correlation.py     ← Correlaciones y significancia
│   │   └── segmentation.py    ← RFM + K-Means
│   │
│   ├── visualization/         ← Capa de presentación
│   │   ├── style.py           ← Tema global y guardado de figuras
│   │   ├── static_plots.py    ← Gráficas Matplotlib/Seaborn
│   │   └── interactive_plots.py ← Dashboards Plotly (HTML)
│   │
│   └── utils/                 ← Utilidades transversales
│       ├── logger.py          ← Logging configurable
│       └── helpers.py         ← Cronómetro, formato moneda, resúmenes
│
├── scripts/
│   └── run_pipeline.py        ← 🚀 Pipeline de extremo a extremo
│
├── notebooks/
│   └── 01_analisis_exploratorio.ipynb ← Recorrido guiado interactivo
│
├── tests/                     ← Suite de pruebas pytest
│   ├── test_generator.py
│   ├── test_cleaner.py
│   ├── test_descriptive.py
│   ├── test_temporal.py
│   └── test_segmentation.py
│
├── data/
│   ├── raw/                   ← Datos generados sin tratar (CSV)
│   └── processed/             ← Datos limpios y enriquecidos (CSV)
│
├── reports/
│   ├── figures/               ← Gráficas PNG + dashboards HTML
│   ├── kpis.json              ← Indicadores clave en JSON
│   └── *.csv                  ← Tablas de resumen exportadas
│
└── logs/
    └── pipeline.log           ← Registro de ejecución
```

---

## ⚙️ Requisitos previos

| Software | Versión mínima | Notas |
|---|---|---|
| Python | 3.10+ | Probado con 3.12 y 3.14 |
| pip | 23+ | Viene incluido con Python |
| Git | opcional | Para clonar/contribuir |
| Navegador | cualquiera | Para ver los dashboards HTML interactivos |

---

## 📥 Instalación

### 1. Clona o descarga el proyecto

```bash
git clone <url-del-repositorio> proyecto-analisis-datos
cd proyecto-analisis-datos
```

*(Si lo descargaste como ZIP, simplemente descomprímelo y entra en la carpeta.)*

### 2. Crea un entorno virtual (muy recomendado)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> 💡 Si PowerShell bloquea la activación, ejecuta antes:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Instala las dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Para desarrollo (tests, formateo, linting):

```bash
pip install -r requirements-dev.txt
```

### 4. (Opcional) Instala el paquete en modo editable

Permite importar `retail_analytics` desde cualquier parte:

```bash
pip install -e .
```

---

## 🚀 Uso rápido

### Ejecutar el pipeline completo

```bash
python scripts/run_pipeline.py
```

En unos segundos verás el progreso paso a paso en consola y se generará:

```text
data/raw/ventas_raw.csv                 ← 12 000 transacciones sintéticas
data/processed/ventas_limpio.csv        ← Dataset limpio + variables derivadas
reports/kpis.json                       ← Facturación, ticket medio, satisfacción…
reports/resumen_categoria.csv           ← Ingresos por categoría de producto
reports/top_productos.csv               ← Ranking de productos
reports/correlaciones_significativas.csv
reports/rfm_segmentos.csv               ← Cada cliente con su segmento
reports/perfiles_segmentos.csv          ← Perfil medio de cada segmento
reports/figures/*.png                   ← 11 gráficas de alta resolución
reports/figures/*.html                  ← 3 dashboards interactivos
logs/pipeline.log                       ← Registro completo de la ejecución
```

### Opciones disponibles

```bash
python scripts/run_pipeline.py --help

--transacciones 12000      # nº de ventas a generar
--clientes 1500            # nº de clientes únicos
--inicio 2024-01-01        # fecha inicial del histórico
--fin 2025-12-31           # fecha final del histórico
--seed 42                  # semilla aleatoria (reproducibilidad)
--sin-interactivas         # omite los HTML de Plotly (ejecución más rápida)
```

Ejemplo de ejecución ligera para pruebas:

```bash
python scripts/run_pipeline.py --transacciones 2000 --clientes 300
```

### Explorar el notebook educativo

```bash
jupyter lab notebooks/01_analisis_exploratorio.ipynb
```

---

## 📦 Módulos documentados

| Módulo | Funciones principales | Qué hace |
|---|---|---|
| `config.py` | `asegurar_directorios` | Centraliza rutas, semilla, catálogo, paleta de colores |
| `data/generator.py` | `generar_ventas`, `generar_clientes`, `guardar_csv` | Crea datos sintéticos con patrones realistas |
| `data/loader.py` | `cargar_csv`, `validar_columnas` | Lee CSV validando esquema y tipos |
| `data/cleaner.py` | `limpiar_ventas`, `agregar_variables`, `resumen_calidad` | Duplicados, nulos, atípicos IQR, variables temporales |
| `analysis/descriptive.py` | `calcular_kpis`, `resumen_por_categoria`, `top_productos` | KPIs y tablas descriptivas |
| `analysis/temporal.py` | `serie_mensual`, `media_movil`, `descomposicion_estacional` | Tendencia, estacionalidad, crecimiento interanual |
| `analysis/correlation.py` | `matriz_correlacion`, `correlaciones_significativas` | Pearson/Spearman + p-valores |
| `analysis/segmentation.py` | `calcular_rfm`, `metodo_codo`, `ajustar_kmeans`, `perfil_segmentos` | Segmentación ML de clientes |
| `visualization/style.py` | `aplicar_estilo`, `guardar_figura` | Tema corporativo y exportación PNG |
| `visualization/static_plots.py` | 11 funciones `grafico_*` | Histogramas, heatmaps, series, clusters… |
| `visualization/interactive_plots.py` | `linea_interactiva`, `sunburst_categorias`… | Dashboards HTML con zoom y filtros |
| `utils/logger.py` | `configurar_logger` | Logs a consola y archivo |
| `utils/helpers.py` | `cronometrar`, `formatear_moneda`, `resumen_dataframe` | Utilidades varias |

---

## 🎓 Conceptos educativos que aprenderás

### 1. Calidad de datos (data cleaning)
El 80 % del trabajo de un analista es limpiar datos. Aquí practicarás:
- **Duplicados**: mismas transacciones repetidas (`drop_duplicates`).
- **Nulos**: eliminación vs. imputación con la mediana y cuándo usar cada una.
- **Atípicos (outliers)**: método del **rango intercuartílico (IQR)** — un valor
  es atípico si cae fuera de `[Q1 − 3·IQR, Q3 + 3·IQR]`. Se marca en una columna
  booleana en lugar de borrarse: *decidir > eliminar*.
- **Ingeniería de variables**: año, mes, trimestre, día de la semana, fin de
  semana… las columnas derivadas que alimentan casi cualquier análisis temporal.

### 2. Estadística descriptiva
- Medidas de **posición** (media, mediana, cuartiles) y **dispersión** (desviación típica).
- **Asimetría (skewness)** y **curtosis**: por qué el ticket medio no basta.
- **Tablas dinámicas** con `groupby().agg()` — la navaja suiza de pandas.

### 3. Series temporales
- **Tendencia**: dirección de largo plazo (aquí, crecimiento lineal).
- **Estacionalidad**: patrones que se repiten con periodo fijo (Navidad, fines de semana).
- **Media móvil**: suaviza el ruido para ver la tendencia subyacente.
- **Descomposición aditiva** (`statsmodels`): `serie = tendencia + estacionalidad + residuo`.
- **Crecimiento interanual**: comparar cada mes contra el mismo mes del año anterior.

### 4. Correlación y significancia
- **Pearson**: relación lineal entre variables numéricas (−1 a +1).
- **Spearman**: versión basada en rangos, robusta ante no-linealidad y atípicos.
- **p-valor**: la correlación de una muestra pequeña puede ser casualidad;
  aquí se contrasta formalmente con `scipy.stats`.

### 5. Machine Learning no supervisado
- **RFM**: tres métricas clásicas de marketing — *Recencia* (días desde la última
  compra), *Frecuencia* (nº de compras) y *Valor monetario* (gasto total).
- **K-Means**: agrupa clientes en k segmentos minimizando la varianza intra-grupo.
- **Método del codo**: cómo elegir k mirando la inercia.
- **Coeficiente de silueta**: mide la calidad del clustering (−1 a +1).
- **Interpretación de negocio**: cada clúster recibe nombre accionable
  (Campeones, Leales, Potenciales, En riesgo…).

---

## 🎲 Los datos sintéticos

¿Por qué generar datos en lugar de descargarlos? Porque así el proyecto es
**100 % reproducible y legal**, y además aprendes a modelar fenómenos reales.
El generador inyecta deliberadamente:

| Patrón | Implementación | Efecto visible |
|---|---|---|
| Tendencia de crecimiento | Factor lineal 0.85 → 1.15 | Las ventas suben ~30 % en 2 años |
| Estacionalidad anual | Pesos por mes (dic = ×1.6) | Picos en noviembre-diciembre |
| Estacionalidad semanal | Sábado = ×1.35 | Fines de semana más fuertes |
| Clientes fieles | Pesos Pareto(α=1.5) | El 20 % de clientes ≈ 60 % de compras |
| Descuentos | 18 % de ventas, 5–30 % | Correlación descuento-satisfacción |
| Ruido gaussiano | σ en satisfacción y fechas | Realismo irreducible |

Con `--seed 42` obtendrás **exactamente** los mismos datos en cada ejecución:
así funcionan los experimentos reproducibles.

---

## 🧪 Pruebas automatizadas

La suite valida que el generador produce datos coherentes, que la limpieza
elimina errores plantados y que los cálculos estadísticos son correctos:

```bash
pytest                      # toda la suite
pytest -v                   # modo detallado
pytest --cov=retail_analytics   # con cobertura (requiere pytest-cov)
```

Salida esperada: todos los tests en verde ✅ en menos de 10 segundos.

---

## ✅ Buenas prácticas aplicadas

- **Semillas aleatorias** centralizadas → resultados reproducibles.
- **Configuración única** (`config.py`) → cero valores mágicos dispersos.
- **Type hints** y **docstrings** en todas las funciones públicas.
- **Logging profesional** a consola + archivo rotulado por paso y duración.
- **Encoding `utf-8-sig`** en CSV → los acentos se ven bien incluso en Excel.
- **Backend Matplotlib no interactivo (Agg)** cuando no hay Jupyter → funciona
  en servidores y CI sin pantalla.
- **Separación de responsabilidades**: datos / análisis / visualización / utilidades.
- **Tests unitarios** por capa, con fixtures y datos diminutos para velocidad.

---

## 🗺️ Roadmap

- [ ] Dashboard web con Streamlit o Dash
- [ ] Modelo predictivo de demanda (Prophet / ARIMA)
- [ ] Exportación automática a PDF con `reportlab`
- [ ] Conector a bases de datos SQLite/PostgreSQL
- [ ] Integración continua (GitHub Actions)

---

## 🤝 Contribuir

1. Haz un *fork* del proyecto.
2. Crea tu rama: `git checkout -b feature/mi-mejora`.
3. Ejecuta los tests: `pytest` (deben pasar).
4. Formatea el código: `black . && isort .`.
5. Abre un *Pull Request* describiendo tu cambio.

---

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Consulta [`LICENSE`](LICENSE) para más detalle.

---

## 📚 Recursos recomendados

- [Documentación de pandas](https://pandas.pydata.org/docs/) — manipulación de datos
- [User Guide de Matplotlib](https://matplotlib.org/stable/users/index.html) — gráficas estáticas
- [Galería de Seaborn](https://seaborn.pydata.org/examples/index.html) — inspiración visual
- [Plotly Python](https://plotly.com/python/) — gráficas interactivas
- [scikit-learn: clustering](https://scikit-learn.org/stable/modules/clustering.html) — K-Means y amigos
- [statsmodels: tsa](https://www.statsmodels.org/stable/tsa.html) — series temporales
- [Guía de estilo PEP 8](https://peps.python.org/pep-0008/) — código limpio

---

Hecho con ❤️ y muchas líneas de pandas · *¡Feliz análisis!*
