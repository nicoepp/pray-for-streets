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


def geometry():
    df = gpd.read_file('/home/nico/Downloads/Roads.geojson')
    street_names = df['STREET_NAME'].unique().tolist()
    df = df[['OBJECTID', 'STREET_NAME', 'ROAD_CLASSIFICATION', 'FROM_STREET',
             'TO_STREET', 'YEAR_CONSTRUCTED', 'DEACTIVATION_DATE', 'geometry']]
    for street in street_names:
        if not street or street == 'N/A':
            continue
        norm_street = street.lower().replace(' ', '_').replace('/', '_')
        df2 = df[df['STREET_NAME'] == street]
        with open(f'public/data/streets/{norm_street}.geo.json', 'w+') as f:
            f.write(df2.to_json())


def all_geo_in_one_file():
    df = gpd.read_file('/home/nico/Downloads/Roads.geojson')
    df2 = df[['STREET_NAME', 'geometry']]
    with open('/home/nico/Downloads/CompactRoads.geo.json', 'w+') as f:
        f.write(df2.to_json())


if __name__ == '__main__':
    all_geo_in_one_file()
