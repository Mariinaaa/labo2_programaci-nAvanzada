# Laboratorio 2 · Gastos personales

Análisis de calidad, limpieza, exploración y preparación para modelado de un conjunto de 10.000 registros de gastos personales. Incluye un dashboard opcional con Shiny.

Los datos originales proceden de [Personal Expense Data](https://www.kaggle.com/datasets/sanjay3454chauhan/personal-expense-data). Sus patrones sugieren que podrían ser sintéticos, por lo que las conclusiones no deben generalizarse a una población real.

## Archivos

- [Notebook resuelto](lab2_gastos_personales-solved.ipynb): análisis y respuestas.
- [Enunciado](Laboratorio2_enunciado.pdf).
- [Datos originales](data/raw/personal_spending_dataset.csv).
- [Datos limpios](data/processed/gastos_limpio.csv).
- [Entrenamiento](data/processed/modelado/train.csv) y [prueba](data/processed/modelado/test.csv): conjuntos transformados.
- [Dashboard](src/app_shiny.py).
- [Notebook inicial](src/lab2_gastos_personales.ipynb): plantilla sin resolver.

## Instalación

Los pasos siguientes se han probado con Python 3.12. En una terminal abierta en la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En macOS o Linux:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

No es necesario activar el entorno si se usa directamente su ejecutable.

## Ejecutar el notebook

En VS Code, abre `lab2_gastos_personales-solved.ipynb`, selecciona el kernel de `.venv` y ejecuta las celdas en orden. También puedes iniciar JupyterLab desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab
```

En macOS o Linux utiliza `./.venv/bin/python -m jupyterlab`. El notebook busca el proyecto desde el directorio de trabajo y sus carpetas superiores; ejecútalo desde la raíz o una subcarpeta. Sus celdas guardan los archivos de `data/processed/` y sobrescriben el dashboard de `src` con el código incluido en el notebook.

## Dashboard

Después de ejecutar el notebook, desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m shiny run src\app_shiny.py
```

En macOS o Linux utiliza `./.venv/bin/python -m shiny run src/app_shiny.py`. Abre la dirección mostrada en la terminal, normalmente http://127.0.0.1:8000, y pulsa `Ctrl+C` para detener el servidor.

## Decisiones principales

Se conservan los registros con posibles problemas y se añaden marcas de calidad para poder filtrarlos. Las variables categóricas se codifican y las numéricas se escalan ajustando las transformaciones solo con entrenamiento. La regresión exploratoria se evalúa con un conjunto de prueba separado y excluye las puntuaciones iguales a cero.
