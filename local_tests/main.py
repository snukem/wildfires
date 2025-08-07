import marimo

__generated_with = "0.14.16"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import openmeteo_requests
    import pandas as pd
    import requests_cache
    from retry_requests import retry

    return mo, openmeteo_requests, pd, requests_cache, retry


@app.cell
def _(openmeteo_requests, requests_cache, retry):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
    	"latitude": 39.1452,
    	"longitude": -120.0957,
    	"start_date": "2025-07-30",
    	"end_date": "2025-08-05",
    	"hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
    	"temperature_unit": "fahrenheit",
    	"wind_speed_unit": "mph",
    }
    responses = openmeteo.weather_api(url, params=params)
    return (responses,)


@app.cell
def _(pd, responses):

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
    	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
    	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = hourly.Interval()),
    	inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""1.  **Define a geographic grid** of latitude and longitude points that covers the state.""")
    return


@app.cell(hide_code=True)
def _():
    return


@app.cell
def _():
    import geopandas as gpd
    import numpy as np
    import matplotlib.pyplot as plt
    from shapely.geometry import Point

    return Point, gpd, np


@app.cell
def _(gpd):
    # Load the shapefile with GeoPolars
    shp_path = "../data/ca_geo/CA_State.shp"
    ca_gdf=gpd.read_file("https://www.naturalearthdata.com/downloads/110m-cultural-vectors/")

    # ensure the CRS is what we expect (WGS84 for lat/lon)
    # * CRS: Coordinate Reference System
    # * WGS 84: World Geodetic System 1984 (EPSG:4326)
    # ca_gdf = ca_gdf.to_crs(epsg=4326)
    # ca_gdf.in
    return (ca_gdf,)


@app.cell
def _(ca_gdf):
    # Get the polygon representing California's boundary
    ca_boundary = ca_gdf.union_all()
    ca_boundary
    return (ca_boundary,)


@app.cell
def _(ca_boundary):
    # Create and filter the grid
    # Create points for the bounding box of the entire state
    min_lon, min_lat, max_lon, max_lat = ca_boundary.bounds

    print('The min and max longitude values in CA are:')
    print(tuple(float("{:.5f}".format(x)) for x in (min_lon, max_lon)))

    print('The min and max latitude values in CA are:')
    print(tuple(float("{:.5f}".format(x)) for x in (min_lat, max_lat)))
    return max_lat, max_lon, min_lat, min_lon


@app.cell
def _():
    # Set the grid resolution in degrees, which represents
    # a distance that varies based on how far north of the 
    # equator you are. At Lat:38N, there is approx 50-60mi
    # between longitudinal degrees; at Lon:-120 latitudinal
    # width is approx 70 mi. So 0.5 aims for ~10 mile blocks
    resolution = 0.2
    return (resolution,)


@app.cell
def _(max_lat, max_lon, min_lat, min_lon, np, resolution):
    # Create a grid that covers the entire bounding box

    # each axis separately
    lon_points = np.arange(min_lon, max_lon, resolution)
    lat_points = np.arange(min_lat, max_lat, resolution)

    # create meshgrid, which returns a tuple of coordinate
    # matrices from coordinate vectors; i.e. makes n-D coordinate
    # arrays to vectorize evaluations
    candidate_points = np.array(np.meshgrid(lon_points, lat_points)).T.reshape(-1, 2)

    candidate_points

    return (candidate_points,)


@app.cell
def _(Point, candidate_points, gpd):
    # Create a GeoDataFrame from the candidate points
    points_gdf = gpd.GeoDataFrame(
        geometry=[Point(lon, lat) for lon, lat in candidate_points],
        crs='EPSG:4326'
    )

    points_gdf
    return (points_gdf,)


@app.cell
def _(ca_gdf, gpd, points_gdf):
    # Use a spatial join to efficiently find all points that 
    # are within the boundary
    points_ca = gpd.sjoin(points_gdf, ca_gdf)
    return


if __name__ == "__main__":
    app.run()
