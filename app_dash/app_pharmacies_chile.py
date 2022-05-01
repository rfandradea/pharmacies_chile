# Libraries
# ==============================================================================

# system
import sys
from pathlib import Path

from sqlalchemy import column

base_path = Path(__file__).parent
path_funciones = (base_path / "assets/").resolve()
sys.path.insert(1, str(path_funciones))

sys.path

# personal functions
import functions_dash as fun

# dashboard
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign
import plotly.graph_objects as go

# data
import pandas as pd
import numpy as np
from requests import options

# import data
# ==============================================================================
data = pd.read_csv('../data/data.csv')

# filters
# ==============================================================================
region_values = sorted(data['region_nombre'].unique())
region_options = fun.options_dropdown(
    labels = region_values
)

options_pharmacies_on_shift = fun.options_dropdown(
    labels = data['turno'].unique()
)

geojson_filter = assign("function(feature, context){return context.props.hideout.includes(feature.properties.name);}")

# IDS
# ==============================================================================
LAT_LNG_ID = 'lat-lng-map'

# Creation app
# ==============================================================================
app = Dash()

# Layout app
# ==============================================================================
app.layout = html.Div(
    [
        html.Div(
            html.H1(
                'FARMACIAS CHILE',
            ),
            className = 'container-div'
        ),

        html.Div(
            [
                html.P('Región'),
                dcc.Checklist(
                    id = 'options-region-name',
                    options = region_options,
                    value = region_values
                ),

                html.P('Comuna'),
                dcc.Dropdown(
                    id = 'options-communes-name',
                    placeholder = 'Seleccione una comuna'
                ),

                html.P('Farmacia'),
                dcc.Dropdown(
                    id = 'options-pharmacies-name'
                ),
        
                html.P('En turno?'),
                dcc.Dropdown(
                    id = 'options-pharmacies-on-shift',
                    options = options_pharmacies_on_shift
                )
            ],
            className = 'selector-container-region'
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.P('Total de Farmacias'),
                        html.Div(
                            id = 'numbers-pharmacies'
                        )
                    ],
                    className = 'card-pharmacies'
                ),

                html.Div(
                    [
                        html.P('Total de Farmacias de Turno'),
                        html.Div(
                            id = 'numbers-pharmacies-on-shift'
                        )
                    ],
                    className = 'card-pharmacies'
                ),

            ]
        ),

        html.Div(
            dl.Map(children = 
                    [
                        dl.TileLayer(url = 'https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}'), 
                        dl.GeoJSON(
                            id = 'geojson', 
                            zoomToBounds = True
                        )
                    ],
                    style = {
                        'width': '1000px', 
                        'height': '500px'
                    }
                )
        ),

        html.Div(
            [
                html.P(id = 'name-pharmacie'),
                html.P(id = 'addres-pharmacie'),
                html.P(id = 'phone-pharmacie'),
                html.P(id = 'office_hours-pharmacie'),
                html.P(id = 'shift-pharmacie')
            ]
        )
    ]
)

# Callback
# ==============================================================================
@app.callback(
    Output('options-communes-name', 'options'),
    Output('options-communes-name', 'value'),
    [
        Input('options-region-name', 'value')
    ]
)
def dropdown_communes_name(region):

    print(region)

    communes = data[
        data['region_nombre'].isin(region)
    ]['comuna_nombre'].unique()

    communes_values = sorted(communes)

    communes_options = fun.options_dropdown(
        labels = communes_values
    )

    return communes_options, communes_values

def update_dropdown_communes_name(region, commune):

    commune_update = []

    if commune is None:
        
        commune_update = dropdown_communes_name(region)[1]

    elif type(commune) != list:

        commune_update.append(commune)

    print(f"update: {commune_update}")

    return commune_update

@app.callback(
    Output('numbers-pharmacies', 'children'),
    Output('numbers-pharmacies-on-shift', 'children'),
    [
        Input('options-region-name', 'value'),
        Input('options-communes-name', 'value')
    ]
)
def view_numbers_parmacies(region, commune):

    commune_filter = update_dropdown_communes_name(region, commune)

    print(region, type(region), commune_filter, type(commune_filter))

    if len(region) == 0 or len(commune_filter) == 0:

        numbers_pharmacies = len(data)

        numbers_pharmacies_on_shift = len(
            data[
                data['turno'] == 'Si'
            ]
        )

    else:

        numbers_pharmacies = len(
            data[
                (data['region_nombre'].isin(region)) &
                (data['comuna_nombre'].isin(commune_filter))
            ]
        )

        numbers_pharmacies_on_shift = len(
            data[
                (data['region_nombre'].isin(region)) &
                (data['comuna_nombre'].isin(commune_filter)) &
                (data['turno'] == 'Si')
            ]
        )

    return numbers_pharmacies, numbers_pharmacies_on_shift

@app.callback(
    Output('geojson', 'data'),
    [
        Input('options-region-name', 'value'),
        Input('options-communes-name', 'value')
    ]
)
def data_geojson(region, commune):

    region_filter = fun.value_to_list(region)
    commune_filter = fun.value_to_list(commune)

    data_filtered = data[
        (~data['local_lat'].isnull()) & 
        (data['region_nombre'].isin(region_filter)) &
        (data['comuna_nombre'].isin(commune_filter))
    ]

    pharmacie = []

    for l, lat, lng in zip(
        data_filtered['local_nombre'], 
        pd.to_numeric(data_filtered['local_lat'], errors = 'coerce'), 
        pd.to_numeric(data_filtered['local_lng'], errors = 'coerce')
        ):

        pharmacie.append({'name': l, 'lat' : lat, 'lon' : lng})

    # Generate geojson with a marker for each city and name as tooltip.
    geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in pharmacie])
    # Create javascript function that filters on feature name.

    return geojson

@app.callback(
    Output('name-pharmacie', 'children'),
    Output('addres-pharmacie', 'children'),
    Output('phone-pharmacie', 'children'),
    Output('office_hours-pharmacie', 'children'),
    Output('shift-pharmacie', 'children'),
    [
        Input('options-pharmacies-name', 'value')
    ]
)
def information_pharmacie(pharmacie):

    print(pharmacie)

    if pharmacie is None:

        return 'Seleccione una farmacia para obtener información', '', '', '', ''

    else:
        data_filtered = data[
            data['local_nombre'] == pharmacie
        ]

        pharmacie_name = data_filtered['local_nombre'].values[0]
        pharmacie_address = data_filtered['local_direccion'].values[0]
        pharmacie_phone = data_filtered['local_telefono'].values[0]
        pharmacie_open = data_filtered['funcionamiento_hora_apertura'].values[0][:5]
        pharmacie_close = data_filtered['funcionamiento_hora_cierre'].values[0][:5]
        
        pharmacie_shift = data_filtered['turno'].values[0]
        pharmacie_date = data_filtered['fecha'].values[0]

        if pharmacie_shift == 'Si':

            pharmacie_open_shift = data_filtered['funcionamiento_hora_apertura_turno'].values[0][:5]
            pharmacie_close_shift = data_filtered['funcionamiento_hora_cierre_turno'].values[0][:5]        

            information_shift = f"""
                La farmacia se encuntra de turno hoy {pharmacie_date}

                    Horario turno: {pharmacie_open_shift}-{pharmacie_close_shift}

            """

        else:

            information_shift = f"""
                La farmacia no presenta turno disponible
            """


        name = f'Nombre farmacia: {pharmacie_name}'
        address = f'Dirección: {pharmacie_address}'
        phone = f'Telefono: {pharmacie_phone}'
        office_hours = f'Hora de atención: {pharmacie_open} - {pharmacie_close}'
        shift = f'{information_shift}'        

        return name, address, phone, office_hours, shift

# Run app
# ==============================================================================
if __name__ == '__main__':
    app.run_server()