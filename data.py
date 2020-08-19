import geopandas as gpd
import json


def main():
    # Abbotsford OpenData
    # https://opendata-abbotsford.hub.arcgis.com/datasets/roads/geoservice
    # Under APIs > GeoJSON
    # Use `geopandas` and `geojsonio` for further analysis
    df = gpd.read_file('/home/nico/Downloads/Roads.geojson')
    sr = df['STREET_NAME']
    u = sr.unique()
    f = open('just_streets.json', 'w+')
    json.dump(u.tolist(), f)
    f.close()


if __name__ == '__main__':
    main()
