'''Dashboard de Shiny for Python para explorar los datos de gastos personales.

Lánzalo con: shiny run src/app_shiny.py
'''
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import PercentFormatter
from shiny import App, reactive, render, ui

RUTA_DATOS = Path(__file__).resolve().parent / 'data' / 'processed' / 'gastos_limpio.csv'
NIVELES = ['Low', 'Medium', 'High']
CATEGORIAS_GASTO = {
    'housing_expense': 'Vivienda',
    'food_expense': 'Comida',
    'transport_expense': 'Transporte',
    'entertainment_expense': 'Ocio',
    'shopping_expense': 'Compras',
    'healthcare_expense': 'Salud',
}
VARIABLES_GRUPO = {
    'occupation': 'Ocupación',
    'area': 'Zona',
    'age_group': 'Grupo de edad',
    'income_source': 'Fuente de ingresos',
    'financial_stress': 'Estrés financiero',
    'credit_card_usage': 'Uso de tarjeta',
}

df = pd.read_csv(RUTA_DATOS)
df['financial_stress'] = pd.Categorical(df['financial_stress'], categories=NIVELES, ordered=True)
df['credit_card_usage'] = pd.Categorical(df['credit_card_usage'], categories=NIVELES, ordered=True)
COLUMNAS_FLAG = [c for c in df.columns if c.startswith('flag_')]

sns.set_theme(style='whitegrid')

EDAD_MIN, EDAD_MAX = int(df['age'].min()), int(df['age'].max())

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize('ocupacion', 'Ocupación', sorted(df['occupation'].unique()), multiple=True),
        ui.input_selectize('zona', 'Zona', sorted(df['area'].unique()), multiple=True),
        ui.input_slider('edad', 'Edad', EDAD_MIN, EDAD_MAX, value=(EDAD_MIN, EDAD_MAX)),
        ui.input_checkbox('excluir_marcadas', 'Excluir filas con problemas de calidad', value=False),
        ui.hr(),
        ui.input_select('agrupar', 'Comparar por', VARIABLES_GRUPO, selected='occupation'),
        ui.help_text('Sin selección en Ocupación o Zona se muestran todas.'),
        width=300,
    ),
    ui.layout_columns(
        ui.value_box('Personas', ui.output_text('n_personas')),
        ui.value_box('Ingreso mediano', ui.output_text('ingreso_mediano')),
        ui.value_box('Tasa de ahorro media', ui.output_text('ahorro_medio')),
        ui.value_box('Salud financiera media', ui.output_text('salud_media')),
        fill=False,
    ),
    ui.layout_columns(
        ui.card(ui.card_header('Salud financiera según inversión y fondo de emergencia'), ui.output_plot('grafico_habitos')),
        ui.card(ui.card_header('Proporción del ingreso destinada a cada categoría'), ui.output_plot('grafico_gasto')),
    ),
    ui.layout_columns(
        ui.card(ui.card_header('Tasa de ahorro y salud financiera'), ui.output_plot('grafico_ahorro')),
        ui.card(ui.card_header(ui.output_text('titulo_grupos', inline=True)), ui.output_plot('grafico_grupos')),
    ),
    ui.card(ui.card_header('Resumen por grupo'), ui.output_data_frame('tabla_grupos')),
    title='Gastos personales y salud financiera',
    fillable=False,
)


def sin_datos(ax):
    ax.text(0.5, 0.5, 'Sin datos para los filtros elegidos', ha='center', va='center', transform=ax.transAxes)
    ax.set_axis_off()


def server(input, output, session):
    @reactive.calc
    def seleccion():
        filtro = df['age'].between(*input.edad())
        if input.ocupacion():
            filtro &= df['occupation'].isin(input.ocupacion())
        if input.zona():
            filtro &= df['area'].isin(input.zona())
        if input.excluir_marcadas():
            filtro &= ~df[COLUMNAS_FLAG].any(axis=1)
        return df[filtro]

    @render.text
    def n_personas():
        return f'{len(seleccion()):,}'.replace(',', '.')

    @render.text
    def ingreso_mediano():
        d = seleccion()
        return f"{d['monthly_income'].median():,.0f}".replace(',', '.') if len(d) else '-'

    @render.text
    def ahorro_medio():
        d = seleccion()
        return f"{d['savings_rate'].mean():.1%}" if len(d) else '-'

    @render.text
    def salud_media():
        d = seleccion()
        return f"{d['financial_health_score'].mean():.1f}" if len(d) else '-'

    @render.plot
    def grafico_habitos():
        d = seleccion()
        fig, ax = plt.subplots()
        if d.empty:
            sin_datos(ax)
            return fig
        datos = d.assign(
            investment=d['investment'].map({True: 'Con inversión', False: 'Sin inversión'}),
            emergency_fund=d['emergency_fund'].map({True: 'Sí', False: 'No'}),
        )
        sns.barplot(
            data=datos, x='investment', y='financial_health_score', hue='emergency_fund',
            order=['Sin inversión', 'Con inversión'], hue_order=['No', 'Sí'], errorbar=None, ax=ax,
        )
        ax.set_xlabel('')
        ax.set_ylabel('Salud financiera media')
        ax.legend(title='Fondo de emergencia')
        return fig

    @render.plot
    def grafico_gasto():
        d = seleccion()
        fig, ax = plt.subplots()
        if d.empty:
            sin_datos(ax)
            return fig
        proporciones = d[list(CATEGORIAS_GASTO)].div(d['monthly_income'], axis=0).rename(columns=CATEGORIAS_GASTO)
        sns.boxplot(data=proporciones, orient='h', ax=ax)
        ax.xaxis.set_major_formatter(PercentFormatter(1))
        ax.set_xlabel('% del ingreso mensual')
        return fig

    @render.plot
    def grafico_ahorro():
        d = seleccion()
        fig, ax = plt.subplots()
        if d.empty:
            sin_datos(ax)
            return fig
        muestra = d.sample(min(len(d), 2000), random_state=42)
        sns.scatterplot(
            data=muestra, x='savings_rate', y='financial_health_score', hue='financial_stress',
            hue_order=NIVELES, alpha=0.5, s=15, ax=ax,
        )
        ax.set_xlabel('Tasa de ahorro')
        ax.set_ylabel('Salud financiera')
        ax.legend(title='Estrés')
        return fig

    @render.text
    def titulo_grupos():
        return f'Salud financiera por {VARIABLES_GRUPO[input.agrupar()].lower()}'

    @render.plot
    def grafico_grupos():
        d = seleccion()
        fig, ax = plt.subplots()
        if d.empty:
            sin_datos(ax)
            return fig
        sns.boxplot(data=d, x=input.agrupar(), y='financial_health_score', ax=ax)
        ax.set_xlabel(VARIABLES_GRUPO[input.agrupar()])
        ax.set_ylabel('Salud financiera')
        ax.tick_params(axis='x', rotation=20)
        return fig

    @render.data_frame
    def tabla_grupos():
        grupo = input.agrupar()
        d = seleccion()
        resumen = (
            d.assign(marcada=d[COLUMNAS_FLAG].any(axis=1))
            .groupby(grupo, observed=True)
            .agg(
                personas=('age', 'size'),
                ingreso_mediano=('monthly_income', 'median'),
                ahorro_medio=('savings_rate', 'mean'),
                deuda_mediana=('debt', 'median'),
                salud_media=('financial_health_score', 'mean'),
                pct_con_problemas=('marcada', 'mean'),
            )
            .assign(pct_con_problemas=lambda r: r['pct_con_problemas'] * 100)
            .round(2)
            .reset_index()
            .rename(columns={grupo: VARIABLES_GRUPO[grupo], 'pct_con_problemas': '% con problemas de calidad'})
        )
        return render.DataGrid(resumen)


app = App(app_ui, server)
