import pandas as pd
import dash
from dash import dcc, html, Input, Output
import numpy as np

data = pd.read_csv("110079-21data121321.csv")
data["Month"] = data['ctvrtletí'] * 3
data["kvartal"] = pd.to_datetime(data.rename(columns={'rok': 'Year'})[['Year', 'Month']].assign(Day=1))
#data = data.query("typosoby_kod == 200")
data.sort_values("kvartal", inplace=True)


app = dash.Dash(__name__)
app.title = "Průměrná mzda - vizualizace"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Vizualizace dat průměrné mzdy a zaměstnanosti", className="header-title"
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Odvětví", className="menu-title"),
                        dcc.Dropdown(
                            id="odvetvi-filter",
                            options=[
                                {"label": odvetvi, "value": odvetvi}
                                for odvetvi in np.sort(data.dropna().odvetvi_txt.unique())
                            ],
                            value="Stavebnictví",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        dcc.Checklist(
                            id="prepocitane-checkbox",
                            options=['přepočtený'],
                            value=['přepočtený'],
                            className="checker",
                        ),
                    ],
                ),

            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="plat-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",

        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="zamestnanost-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",

        ),

    ]

)


@app.callback(
    [Output("plat-chart", "figure"), Output("zamestnanost-chart", "figure")],

    Input("odvetvi-filter", "value"),
    Input("prepocitane-checkbox", "value"),
)

def update_charts(odvetvi, prepocitane):
    if prepocitane:
        mask = (
            (data.odvetvi_txt == odvetvi)
            & (data.stapro_kod == 5958)
            & (data.typosoby_txt == "přepočtený")
        )
        mask_zam = (
            (data.odvetvi_txt == odvetvi)
            & (data.stapro_kod == 316)
            & (data.typosoby_txt == "přepočtený")
        )
    else:
        mask = (
                (data.odvetvi_txt == odvetvi)
                & (data.stapro_kod == 5958)
                & (data.typosoby_txt == "fyzický")
        )
        mask_zam = (
                (data.odvetvi_txt == odvetvi)
                & (data.stapro_kod == 316)
                & (data.typosoby_txt == "fyzický")
        )
    filtered_data = data.loc[mask, :]
    filtered_data_zam = data.loc[mask_zam, :]
    plat_chart_figure = {
        "data": [
            {
                "x": filtered_data["kvartal"],
                "y": filtered_data["hodnota"],
                "type": "bar",
                "hovertemplate": "%{y:} Kč"
                                 "<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Průměrná mzda",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"ticksuffix": " Kč", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    zamestnanost_chart_figure = {
        "data": [
            {
                "x": filtered_data_zam["kvartal"],
                "y": filtered_data_zam["hodnota"],
                "type": "bar",
                "hovertemplate": "%{y:} tis."
                                 "<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Zaměstnanost",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"ticksuffix": " tis.", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }
    return plat_chart_figure, zamestnanost_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
