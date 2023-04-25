import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import requests

BREEZOMETER_API_KEY = '36fec6eacc224e17969e0a8b9128c7ce'

def get_air_quality_data(latitude, longitude):
    url = f'https://api.breezometer.com/air-quality/v2/current-conditions?lat={latitude}&lon={longitude}&key={BREEZOMETER_API_KEY}'
    response = requests.get(url)
    data = response.json()
    print(data)
    return data

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Air Pollution Heatmap'),
    dcc.Graph(id='heatmap', figure={}),
    html.Div(id='location-info'),
    dcc.Interval(id='interval', interval=60 * 60 * 1000, n_intervals=0)
])

@app.callback(
    dash.dependencies.Output('heatmap', 'figure'),
    [dash.dependencies.Input('interval', 'n_intervals')]
)
def update_heatmap(_):
    center_lat = 0
    center_lon = 0
    zoom = 1

    fig = go.Figure(go.Scattermapbox(
        lat=[center_lat],
        lon=[center_lon],
        mode='markers',
        marker=go.scattermapbox.Marker(size=0)
    ))

    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            zoom=zoom,
            center=dict(lat=center_lat, lon=center_lon),
            layers=[
                dict(
                    sourcetype='raster',
                    source=f'https://tiles.breezometer.com/v1/air-quality/breezometer-aqi/current-conditions/{{z}}/{{x}}/{{y}}.png?key={BREEZOMETER_API_KEY}&breezometer_aqi_color=indiper',
                    type='raster',
                    below='traces'
                )
            ]
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig

@app.callback(
    dash.dependencies.Output('location-info', 'children'),
    [dash.dependencies.Input('heatmap', 'clickData')]
)
def display_location_info(clickData):
    if clickData:
        lat = clickData['points'][0]['lat']
        lon = clickData['points'][0]['lon']
        data = get_air_quality_data(lat, lon)
        if 'data' in data:
            city = data['data']['city']
            country = data['data']['country']
            aqi = data['data']['indexes']['baqi']['value']
            return f'City: {city}, Country: {country}, AQI: {aqi}'
        else:
            return 'Unable to fetch air quality data for the clicked location'
    else:
        return 'Click on the heatmap to display air quality information'

if __name__ == '__main__':
    app.run_server(debug=True)
