import dash
from dash import html, dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import date
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from plotly.subplots import make_subplots
from analytics import Analytic

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)

# Inicijalizacija Dash-a
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
server = app.server
# Inicijalizacija Dash boostrap tema
theme_change = ThemeChangerAIO(aio_id="theme", radio_props={"value":dbc.themes.MORPH})

analytic = Analytic()

figPie = make_subplots(
    rows=1, 
    cols=4, 
    subplot_titles=['Odrzanih intervjua', 'Primljenih kandidata', 'Pristali na obuku', 'Odbili obuku'], 
    specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}]]
    )

app.layout = html.Div([

    dbc.Container([theme_change], className="m-4 dbc"),

    html.H1("Statistika", style={"font-size": "60px", "padding": "30px"}),
    html.Label("Izaberi podatke za analiziranje:", style={"font-weight": "bold", "padding": "10px"}),
        dcc.Dropdown(
        id = "dropdown-column1",
        options=[
            {"label": "Komercijala", "value": "Komercijala"},
            {"label": "Telemarketing", "value": "Telemarketing"}
        ],
        style={"color": "black"},
        className="m-1",
        value=None,
        placeholder="Izaberi podatke za analiziranje.."
    ),
    html.Label("Izaberi rukovodilca:", style={"font-weight": "bold", "padding": "10px"}),
    dcc.Dropdown(
        id="dropdown-column2",
        options=[],
        style={"color": "black"},
        className="m-1",
        value=None,
        placeholder="Izaberi rukovodilca.."
    ),
    html.Label("Izaberi opseg datuma:", style={"font-weight": "bold", "padding": "10px"}),
    dcc.DatePickerRange(
        id="date-picker-range",
        start_date_placeholder_text="Datum od",
        end_date_placeholder_text="Datum do",
        calendar_orientation='vertical',
        style={"padding": "10px"}
    ),
    
    dcc.Graph(id="line-plot", className="m-4", style={"width": "94.9%"}),

    html.H2("Odnos", style={"font-size": "60px", "padding": "30px"}),
    dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(id='pie-graph', className="m-4", style={"width": "90%"}), md=3),
            dbc.Col(dcc.Graph(id='pie-graph1', className="m-4", style={"width": "90%"}), md=3),
            dbc.Col(dcc.Graph(id='pie-graph2', className="m-4", style={"width": "90%"}), md=3),
            dbc.Col(dcc.Graph(id='pie-graph3', className="m-4", style={"width": "90%"}), md=3),
        ], className="flex-row flex-wrap")
    ], fluid=True)


], style={"display": "flex", "flexDirection": "column","flexWrap": "wrap"}, className="BABA")


@app.callback(
    Output("dropdown-column2", "options"),
    Input("dropdown-column1", "value")
)
def update_drop_down_column2(selected_value):
    
    # Alociramo datoteke
    analytic.locate_data()

    # Biramo koji excel sheet se analizira
    analytic.load_data(selected_value)

    # Pozivanje cistih podataka
    rukovodilac = analytic.clean()

    # Postoje samo dve moguce opcije ako input nije onda vrati praznu listu za options
    if selected_value in ["Komercijala", "Telemarketing"]:

        rukovodilac = rukovodilac[rukovodilac["Rukovodilac"].notna()]["Rukovodilac"].unique()

    else:

        rukovodilac = []

    # Ako postoje imena vracamo opcije u suprotnom []
    options = [{"label": ruk, "value": ruk} for ruk in rukovodilac]

    return options if options else []

@app.callback(
    Output("line-plot", "figure"),
    [
        Input("dropdown-column1", "value"), 
        Input("dropdown-column2", "value"), 
        Input("date-picker-range", "start_date"), 
        Input("date-picker-range", "end_date"),
        Input(ThemeChangerAIO.ids.radio("theme"), "value")
    ]
)
def update_line_plot(selected_column1, selected_column2, start_date, end_date, theme):

    # Prikaz praznog graph-a
    figLine = px.line(template=template_from_url(theme))

    # ZA LINE GRAPH SVE MORA DA BUDE TACNO
    if selected_column1 is not None and selected_column2 is not None and start_date is not None and end_date is not None:

        # Alociramo datoteke
        analytic.locate_data()

        # Biramo koji excel sheet se analizira
        analytic.load_data(selected_column1)

        # Pozivanje cistih podataka
        analytic.clean()

        # Formatiranje datuma
        start_date_object = date.fromisoformat(start_date)
        end_date_object = date.fromisoformat(end_date)

        # Filtriranje po zadatom parametru
        filtr_data = analytic.filter_by_date(
            selected_column2, 
            start_date_object,
            end_date_object
            )
        
        # Ekstraktujemo vrednosti i pakujemo kao [[idx, val], [idx1, val1], ...]
        graph_data = [(idx, val) for idx, val in zip(filtr_data.index, filtr_data.values)]

        # Konvertujemo podatke u novi DataFrame
        df = pd.DataFrame(graph_data, columns=["Datum zakazivanja", "Broj intervjua"])
        
        # Kolonu Datum zakazivanja konvertujemo u pd datetime tip
        df["Datum zakazivanja"] = pd.to_datetime(df["Datum zakazivanja"])

        intervju_sum = df["Broj intervjua"].sum()

        # Ubacujemo varibialne podatke u graph i temu ako je primenjena
        figLine = px.line(
            df, 
            x="Datum zakazivanja", 
            y="Broj intervjua", 
            title=f"Grafikon za {selected_column2} | Ukupan broj intervjua je {intervju_sum} za zadati datum: {start_date_object} / {end_date_object}",
            template=template_from_url(theme),
            markers=True
        )

        return figLine
    
    # Ako nije ispunjen uslov vrati prazan graph a ako je odabran tema primeni je
    else:
    
        return figLine.update_layout(title="No Data Available",template=template_from_url(theme))

@app.callback(
    Output('pie-graph', 'figure'),
    Output('pie-graph1', 'figure'),
    Output('pie-graph2', 'figure'),
    Output('pie-graph3', 'figure'),
    [
        Input("dropdown-column1", "value"),
        Input("date-picker-range", "start_date"), 
        Input("date-picker-range", "end_date"),
        Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    ]
)
def update_pie_chart(selected_column1, start_date, end_date, theme):

    if selected_column1 is not None and start_date is not None and end_date is not None:
        
        # Alociramo datoteke
        analytic.locate_data()

        # Biramo koji excel sheet se analizira
        analytic.load_data(selected_column1)

        # Pozivanje cistih podataka
        analytic.clean()

        # Formatiranje datuma
        start_date_object = date.fromisoformat(start_date)
        end_date_object = date.fromisoformat(end_date)

        filtr_data = analytic.pie_data(start_date_object, end_date_object)

        labels = list(filtr_data[0].keys())

        values = list(filtr_data[0].values())
        values1 = list(filtr_data[1].values())
        values2 = list(filtr_data[2].values())
        values3 = list(filtr_data[3].values())

        # Dodajemo podatke za pie graph
        figPie = px.pie(
            names=labels, 
            values=values,
            title='Ukupan broj intervjua',
            template=template_from_url(theme),
        )
        figPie1 = px.pie(
            names=labels, 
            values=values1,
            title='Ukupan broj primljenih',
            template=template_from_url(theme),
        )
        figPie2 = px.pie(
            names=labels, 
            values=values2,
            title='Pristali na obuku',
            template=template_from_url(theme),
        )
        figPie3 = px.pie(
            names=labels, 
            values=values3,
            title='Odbili obuku',
            template=template_from_url(theme),
        )

        return figPie, figPie1, figPie2, figPie3
    
    else:
        # Ako uslov nije zadovoljen vracamo prazan pie graph sa No data porukom 
        figPie = px.pie(
            names=["No Data"], 
            values=[100],
            title='No Data Available',
            template=template_from_url(theme),
        )
        figPie1 = px.pie(
            names=["No Data1"], 
            values=[100],
            title='No Data Available1',
            template=template_from_url(theme),
        )
        figPie2 = px.pie(
            names=["No Data1"], 
            values=[100],
            title='No Data Available2',
            template=template_from_url(theme),
        )
        figPie3 = px.pie(
            names=["No Data3"], 
            values=[100],
            title='No Data Available3',
            template=template_from_url(theme),
        )

        return figPie, figPie1, figPie2, figPie3

# Pokretanje servera
if __name__ == "__main__":

    app.run_server(debug=True)