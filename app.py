from flask import Flask, render_template, request, jsonify
import requests
import json
import plotly.graph_objects as go
import dash
import dash_leaflet as dl
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
#import dash_table
import plotly.express as px
from dash.exceptions import PreventUpdate
import mapbox
import config
import os

app = Flask(__name__)


# Mapbox API key and Breezometer API key, I have hidden the keys in github secrets as they are private
mapbox_token = config.MAPBOX_API_KEY
breezometer_token = config.BREEZOMETER_API_KEY
geocoding = mapbox.Geocoder(access_token=mapbox_token)



dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])




#Flask App with Air Pollution map on HTML and Javascript
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/javascript_map')
def javascriptmap():
    return render_template('javascript_map.html')

@app.route('/search_location', methods=['POST'])
def search_location():
    query = request.form.get('query')
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={mapbox_token}"
    response = requests.get(url)
    data = response.json()
    return jsonify(data)


@app.route('/get_air_quality', methods=['POST'])
def get_air_quality():
    lat = request.form['lat']
    lon = request.form['lon']
    url = f'https://api.breezometer.com/air-quality/v2/current-conditions?lat={lat}&lon={lon}&key={breezometer_token}&features=breezometer_aqi'
    response = requests.get(url)
    data = response.json()

    return jsonify(data)

#Flask App with Plotly map for Air Pollution
@app.route('/plotly_map')
def plotly_map():
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        mode='markers+text',
        lon=[0], lat=[0],
        marker=go.scattermapbox.Marker(size=9)
    ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            accesstoken=mapbox_token,
            bearing=0,
            center=dict(
                lat=45,
                lon=0
            ),
            pitch=0,
            zoom=3,
            style='light',
            layers=[
                dict(
                    sourcetype='raster',
                    source=[
                        f'https://tiles.breezometer.com/v1/air-quality/breezometer-aqi/current-conditions/{{z}}/{{x}}/{{y}}.png?key={breezometer_token}&breezometer_aqi_color=indiper'
                    ],
                    type='raster',
                    below='traces',
                    opacity=0.6
                )
            ]
        ),
    )

    plot_html = fig.to_html(full_html=False)
    return render_template('plotly_map.html', plot=plot_html)

# Dash Leaflet App for Air Pollution (All code below is Python)

mapbox_tile_layer = dl.TileLayer(
    url=f'https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_token}',
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom=20,
    minZoom=2,
    tileSize=512,
    zoomOffset=-1
)

breezometer_tile_layer = dl.TileLayer(
    url=f'https://tiles.breezometer.com/v1/air-quality/breezometer-aqi/current-conditions/{{z}}/{{x}}/{{y}}.png?key={breezometer_token}&breezometer_aqi_color=indiper',
    attribution='&copy; <a href="https://www.breezometer.com/">Breezometer</a>',
    maxZoom=20,
    minZoom=2,
    tileSize=512,
    zoomOffset=-1,
    opacity=0.6  # Set opacity to 60% for breezometer heatmap tiles
)

dash_app.layout = html.Div([
    html.H1("Air Pollution - Heatmap & Realtime data", style={'width': '100%', 'height': '10vh', 'margin': 'auto', 'text-align': 'center', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
    dash_table.DataTable(
        id="pollutants-table",
        columns=[
            {"name": "Pollutant", "id": "display_name"},
            {"name": "AQI", "id": "aqi"},
            {"name": "Concentration", "id": "concentration"},
            {"name": "units", "id": "concentration_units"},
        ],
        style_cell={
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_table={
            "position": "absolute",
            "top": "15vh",
            "left": "2vw",
            "width": "auto",
            "zIndex": 1000,
            "backgroundColor": "white",
            "padding": "10px",
            "opacity": "0.8",
        },
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
    ),
    html.Div([  # Wrap the search box in a html.Div component
            dbc.Input(
                id="search-box",
                type="text",
                placeholder="Search location...",
                style={
                    "position": "absolute",
                    "top": "10px",
                    "left": "50%",
                    "transform": "translateX(-50%)",
                    "width": "50%",
                    "zIndex": 1000
                }
            )
        ], style={"position": "absolute", "width": "100%", "height": "100%"}),
    dl.Map([
        dl.LayersControl(
            [
                dl.BaseLayer(mapbox_tile_layer, name="Mapbox Streets", checked=True),
                dl.Overlay(breezometer_tile_layer, name="BreezoMeter Heatmap", checked=True),
            ]
        ),
        dl.MarkerClusterGroup(id="marker-group"),
        html.Div([  # Wrap the legend in a dl.Div component
            html.Img(
                src=dash_app.get_asset_url("legend.png"),
                style={
                    "position": "absolute",
                    "bottom": "10px",
                    "right": "10px",
                    "zIndex": 1000,
                    "width": "250px",
                }
            )
        ], style={"position": "absolute", "width": "100%", "height": "100%"}),
        #dl.Popup(id="map-popup"),
        
        
    ], id="map", style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"}, 
    center=[33.4232, -111.9344], zoom=6),
    dcc.Graph(id="forecast-plot", style={
        "position": "absolute",
        "bottom": "10vh",
        "left": "2vw",
        "width": "30%",
        "height": "30%",
        "zIndex": 1000,
        "opacity": "0.8"
    }),
    html.Div(id="click-coordinates"),
    html.Footer(
        children=[
        html.P([
            "The Air Quality displayed here is ",
            html.A("Breezometer", href="https://www.breezometer.com", target="_blank", style={"textDecoration": "none"}),
            " Air Quality Index (BAQI)"], style={"fontSize": "14px"})],
        style={
            'width': '100%',
            'position': 'fixed',
            'bottom': '5px',
            'text-align': 'center',
            'display': 'flex',
            'justify-content': 'center',
            'align-items': 'center'
        }
    )
])



@dash_app.callback(
    [Output("map", "center"), Output("map", "zoom"), Output("map", "click_lat_lng")],
    Input("search-box", "n_submit"),
    Input("search-box", "n_blur"),
    State("search-box", "value"),
)
def search_location(n_submit, n_blur, search_value):
    if not search_value:
        raise PreventUpdate

    # Perform geocoding
    response = geocoding.forward(search_value)
    if response.status_code == 200 and response.geojson()['features']:
        feature = response.geojson()['features'][0]
        lat, lon = feature['geometry']['coordinates'][::-1]
        return [lat, lon], 15, [lat, lon]
    else:
        raise PreventUpdate


@dash_app.callback(
    Output("forecast-plot", "figure"),
    Input("map", "click_lat_lng"),
)
def update_forecast_plot(click_lat_lng):
    if click_lat_lng is None:
        raise PreventUpdate

    lat, lon = click_lat_lng

    # Set the number of hours for the forecast
    hours = 24

    # Fetch the forecast data
    response = requests.get(
        f"https://api.breezometer.com/air-quality/v2/forecast/hourly?lat={lat}&lon={lon}&key={breezometer_token}&hours={hours}"
    )
    data = response.json()

    # Check if the data key exists in the response
    if data.get("data") is None:
        raise PreventUpdate

    # Extract the forecast hours and AQI values
    forecast_hours = [entry["datetime"] for entry in data["data"]]
    aqi_values = [entry["indexes"]["baqi"]["aqi"] for entry in data["data"]]

    # Create a Plotly line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_hours, y=aqi_values, mode='lines'))
    fig.update_layout(
        title="Hourly Forecast",
        xaxis_title="Hour",
        yaxis_title="AQI",
        margin=dict(l=0, r=0, t=30, b=0),
        autosize=True,
    )

    return fig



@dash_app.callback(
    Output("marker-group", "children"),
    Output("click-coordinates", "children"),
    Output("pollutants-table", "data"),
    #Output("map-popup", "children"),
    Input("map", "click_lat_lng"),
)
def add_marker_and_show_coordinates(click_lat_lng):

    ctx = dash.callback_context
    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0]
    pollutants_info = []

    if click_lat_lng is None:
        return None, "Click on the map to get the coordinates"
    elif triggered_input == "search-box":
        return None, None
    else:
        lat, lon = click_lat_lng
        response = requests.get(
            f"https://api.breezometer.com/air-quality/v2/current-conditions?lat={lat}&lon={lon}&key={breezometer_token}&features=breezometer_aqi,pollutants_concentrations,pollutants_aqi_information"
        )
        data = response.json()
        if data.get("error"):
            air_quality_info = "Air quality data not available"
        else:
            indexes = data["data"]["indexes"]
            if "baqi" in indexes:
                aqi = indexes["baqi"]["aqi"]
                category = indexes["baqi"]["category"]
                dominant_pollutant = indexes["baqi"]["dominant_pollutant"]
                air_quality_info = f"Air Quality Index (AQI): {aqi}, Category: {category}, Dominant Pollutant: {dominant_pollutant}"
                
                
            else:
                air_quality_info = "Air quality data not available"

            pollutants = data["data"]["pollutants"]
            pollutants_info = []
            for key, value in pollutants.items():
                    pollutants_info.append({
                        "name": key,
                        "display_name": value["display_name"],
                        "aqi": value["aqi_information"]["baqi"]["aqi"] if value["aqi_information"] else None,
                        "concentration": value["concentration"]["value"],
                        "concentration_units": value["concentration"]["units"],
                    })
        df = pd.DataFrame(pollutants_info)
        # Reverse geocoding using Mapbox API
        geocoding_response = geocoding.reverse(lon=lon, lat=lat)
        if geocoding_response.status_code == 200 and geocoding_response.geojson()['features']:
            feature = geocoding_response.geojson()['features'][0]
            location = feature['place_name']
        else:
            location = "Location not found"

        marker=dl.Marker(
                position=click_lat_lng,
                children=[dl.Popup(
                    children=html.Div([
                        html.P(location),  # Display location, state, and country
                        html.P(air_quality_info)
                    ]), closeOnClick=False, autoPan=True, keepInView=True
                ),]
            )
        return [marker
            
        ], f"coordinates: {lat:.4f}, {lon:.4f}", df.to_dict("records")


if __name__ == '__main__':
    app.run(debug=True)
