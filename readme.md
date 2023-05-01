
# Air Pollution Heatmap

This is a web application that visualizes air pollution data in the form of an interactive heatmap. The application is built using Python, Flask, and a variety of other tools and libraries.

## Features

- Display air pollution data from various sources in a heatmap format
- Filter data based on pollutant type, date range, and geographical area
- Interactive map allowing users to zoom and pan to explore the data
- Responsive design for desktop and mobile devices

## Installation

1. Clone the repository:
git clone https://github.com/PavanKumarGurram/air-pollution-heatmap.git

2. Change to the project directory:
cd air-pollution-heatmap

3. Create a virtual environment and activate it:
python3 -m venv venv
source venv/bin/activate

4. Install the required packages:
pip install -r requirements.txt

5. Run the application locally:
python app.py

6. Open your browser and navigate to `http://localhost:5000`.

## Deployment

This application can be deployed on Heroku. To do so, follow the [official Heroku documentation](https://devcenter.heroku.com/articles/getting-started-with-python).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

- [Mapbox API](https://www.mapbox.com/) for providing the mapping and geolocation services
- [Breezometer API](https://breezometer.com/) for providing the air quality data