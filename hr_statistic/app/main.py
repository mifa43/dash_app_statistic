import dash
from dash import html, dcc, dash_table, no_update
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import date
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from plotly.subplots import make_subplots
from analytics import Analytic
from datetime import datetime
import dash_auth
from collections import OrderedDict
from dash.exceptions import PreventUpdate
global lista
lista=[]
VALID_USERNAME_PASSWORD_PAIRS = {
    'mifa43': 'koliko43'
}
dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)

# Inicijalizacija Dash-a
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
server = app.server
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
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
    html.Div([
        
        dcc.DatePickerRange(
            id="date-picker-range",
            start_date_placeholder_text="Datum od",
            end_date_placeholder_text="Datum do",
            calendar_orientation='vertical',
            style={"padding": "10px"}
        ),
        dbc.Button('Klikni me', id='dugme', style={"border-radius": "30px"}, className="m-4 dbc"),
        html.Div(id='ispis'),
    ], className="d-grid gap-2 d-md-flex justify-content-md"),

    dcc.Loading(
        id="loading-after-dropdown1",
        type="default",
        children=html.Div(id="loading-output-1"),
        fullscreen=True
    ),
    dcc.Loading(
        id="loading-before-line-plot",
        type="default",
        children=html.Div(id="loading-output-2"),
        fullscreen=True
    ),
    dcc.Loading(
        id="loading-before-pie-plot",
        type="default",
        children=html.Div(id="loading-output-3"),
        fullscreen=True
    ),
    dcc.Loading(
        id="loading-before-tabel-plot",
        type="default",
        children=html.Div(id="loading-output-4"),
        fullscreen=True
    ),
    dcc.Graph(id="line-plot", className="m-4", style={"width": "94.9%"}),

    html.H2("Odnos intervjua u zadatom vremenskom opsegu", style={"font-size": "60px", "padding": "30px"}),
    dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(id='pie-graph', className="m-3", style={"width": "90%"}), md=3),
            dbc.Col(dcc.Graph(id='pie-graph1', className="m-3", style={"width": "90%"}), md=3),
            dbc.Col(dcc.Graph(id='pie-graph2', className="m-3", style={"width": "90%"}), md=3),
            dbc.Col(dcc.Graph(id='pie-graph3', className="m-3", style={"width": "90%"}), md=3),
        ], className="flex-row flex-wrap")
    ], fluid=True),

    html.Div([
        html.H2("Najcesci razlog odbijanja/odustanka od obuke", style={"font-size": "40px", "padding": "30px"}),
        dash_table.DataTable(
            id='data-table',
            columns=[
                {'name': 'Razlog', 'id': 'Razlog'}, 
                {'name': 'Broj ponavljanja', 'id': 'Broj ponavljanja'}
            ],
            tooltip_delay=0,
            tooltip_duration=None,
            tooltip_data=[],
            filter_action="native",
            row_deletable=True,
            page_action="native",
            page_current= 0,
            page_size= 15,
            style_table={"overflowX": "auto"},
            data=[]  # Postavite praznu listu kao inicijalne podatke
            
        )
        
    ], style={"width": "50%", "padding": "15px"})

], style={"display": "flex", "flexDirection": "column","flexWrap": "wrap"}, className="BABA")


@app.callback(
    Output("dropdown-column2", "options"),
    Output("loading-after-dropdown1", "children"),
    Input("dropdown-column1", "value")
)
def update_drop_down_column2(selected_value):
    if not selected_value:
        raise PreventUpdate

    # Alociramo datoteke
    analytic.locate_data()

    # Biramo koji excel sheet se analizira
    analytic.load_data(selected_value)

    # Pozivanje cistih podataka
    rukovodilac = analytic.clean()

    # Postoje samo dve moguce opcije ako input nije onda vrati praznu listu za options
    if selected_value in ["Komercijala", "Telemarketing"]:
        lista.append("update_drop_down_column2")

        rukovodilac = rukovodilac[rukovodilac["Rukovodilac"].notna()]["Rukovodilac"].unique()

    else:

        rukovodilac = []

    # Ako postoje imena vracamo opcije u suprotnom []
    options = [{"label": ruk, "value": ruk} for ruk in rukovodilac]

    return options if options else [], ""

@app.callback(
    Output("line-plot", "figure"),
    Output("loading-before-line-plot", "children"),
    [
        Input("dropdown-column1", "value"), 
        Input("dropdown-column2", "value"), 
        Input("date-picker-range", "start_date"), 
        Input("date-picker-range", "end_date"),
        Input(ThemeChangerAIO.ids.radio("theme"), "value")
    ],
)
def update_line_plot(selected_column1, selected_column2, start_date, end_date, theme):
    # if not selected_column2:
    #     raise PreventUpdate
    
    global lista
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
        start_date_object = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        end_date_object = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d-%m-%Y")

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
            title=f"Grafikon za rukovodilca: {selected_column2} | Ukupan broj intervjua je {intervju_sum} za zadati datum: {start_date_object} / {end_date_object}",
            template=template_from_url(theme),
            markers=True
        )

        lista.append("update_line_plot")

        return figLine, no_update
    
    # Ako nije ispunjen uslov vrati prazan graph a ako je odabran tema primeni je
    else:

        figLine.update_layout(title="No Data Available",template=template_from_url(theme))

        return figLine, no_update 

@app.callback(
    Output('pie-graph', 'figure'),
    Output('pie-graph1', 'figure'),
    Output('pie-graph2', 'figure'),
    Output('pie-graph3', 'figure'),
    Output("loading-before-pie-plot", "children"),
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
        # Konvertovanje datuma u željeni format
        start_date_object = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        end_date_object = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d-%m-%Y")


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
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )
        figPie1 = px.pie(
            names=labels, 
            values=values1,
            title='Ukupan broj primljenih',
            template=template_from_url(theme),
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )
        figPie2 = px.pie(
            names=labels, 
            values=values2,
            title='Pristali na obuku',
            template=template_from_url(theme),
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )
        figPie3 = px.pie(
            names=labels, 
            values=values3,
            title='Odbili obuku',
            template=template_from_url(theme),
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )
        lista.append("update_pie_chart")
        return figPie, figPie1, figPie2, figPie3, no_update
    
    else:
        # Ako uslov nije zadovoljen vracamo prazan pie graph sa No data porukom 
        figPie = px.pie(
            names=["No Data"], 
            values=[100],
            title='No Data Available',
            template=template_from_url(theme),
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )
        figPie1 = px.pie(
            names=["No Data1"], 
            values=[100],
            title='No Data Available1',
            template=template_from_url(theme),
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )
        figPie2 = px.pie(
            names=["No Data1"], 
            values=[100],
            title='No Data Available2',
            template=template_from_url(theme),
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )
        figPie3 = px.pie(
            names=["No Data3"], 
            values=[100],
            title='No Data Available3',
            template=template_from_url(theme),
            labels={'names': 'Rukovodilac', 'values': 'Broj intervjua'},
        )

        return figPie, figPie1, figPie2, figPie3, no_update
@app.callback(
    Output('data-table', 'data'),
    Output('data-table', 'tooltip_data'),
    Output("loading-before-tabel-plot", "children"),
    [
        Input("dropdown-column1", "value"),
        Input("date-picker-range", "start_date"), 
        Input("date-picker-range", "end_date"),
        Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    ]

)
def update_table(selected_column1, start_date, end_date, theme):
    

    # Proveravamo da li postoje inputi ako ih nema vracamo tabel_data=[], markdown=[]
    if selected_column1 is not None and start_date is not None and end_date is not None:
        # Alociramo datoteke
        analytic.locate_data()

        # Biramo koji excel sheet se analizira
        analytic.load_data(selected_column1)

        # Pozivanje cistih podataka
        analytic.clean()

        # Formatiranje datuma
        # Konvertovanje datuma u željeni format
        start_date_object = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        end_date_object = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d-%m-%Y")

        tabel_data, markdown = analytic.refuse_messages_data(start_date_object, end_date_object)
        lista.append("update_table")

        return tabel_data, markdown, no_update
    
    else:
        
        return [],[], no_update
# Python funkcija koja će se izvršiti kada se klikne dugme
@app.callback(
    Output('ispis', 'children'),
    Input('dugme', 'n_clicks')
)
def ispis_klika(n_clicks):
    if n_clicks is None:
        return "Kliknite dugme..."
    else:
        print(lista)  # Ispisuje u terminalu
        lista.clear()
        return "Kliknuli ste dugme!"

# Pokretanje servera
if __name__ == "__main__":

    app.run_server(debug=True)