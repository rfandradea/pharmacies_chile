# Libraries
# ==============================================================================

# system
from cProfile import label
import sys
from pathlib import Path

base_path = Path(__file__).parent
path_funciones = (base_path / "assets/").resolve()
sys.path.insert(1, str(path_funciones))

sys.path

# personal functions
import functions_dash as fun

# dashboard
import dash
from dash import dcc 
from dash import html

from dash.dependencies import Input, Output, State

# data
import pandas as pd
import numpy as np
from requests import options

# import data
# ==============================================================================
data = pd.read_csv('../data/data.csv')

# filters
# ==============================================================================
options_comuna = fun.options_dropdown(
    labels = sorted(data['comuna_nombre'].unique())
)

# Creation app
# ==============================================================================
app = dash.Dash()

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
                dcc.Dropdown(
                    options = options_comuna, 
                    value = ['SANTIAGO']
                )
            ],
            className = 'selector-container-region'
        )

    ]
)

# Run app
# ==============================================================================
if __name__ == '__main__':
    app.run_server()