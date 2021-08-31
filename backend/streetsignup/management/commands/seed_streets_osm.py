from django.core.management.base import BaseCommand
import json
import osmnx as ox
from backend.streetsignup.models import Street, Segment, City
import geopandas as gp


class Command(BaseCommand):
    help = 'Populates the Street and Segment models fetching data from OpenStreetMaps'

    def add_arguments(self, parser):
        parser.add_argument('city_name', nargs='+', type=str)
        parser.add_argument('province_name', nargs='+', type=str)
        parser.add_argument('city', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['city_name'] or not options['province_name'] or not options['city']:
            print('Please enter all 3 arguments: city_name, province_name and city')
            return
        # place = "City of Langley, British Columbia"
        city_name = options['city_name'][0]
        province_name = options['province_name'][0]
        city_db = options['city'][0]
        place = city_name + ', ' + province_name
        graph = ox.graph_from_place(place, network_type='drive')
        nodes, streets = ox.graph_to_gdfs(graph)
        street_names = streets.name.tolist()
        street_coordinates = streets.geometry.tolist()

        if City.objects.filter(name=city_db).exists():
            c = City.objects.get(name=city_db)
        else:
            c = City.objects.create(name=city_db, province=province_name)
        for i, str_name in enumerate(street_names):
            if isinstance(str_name, list):
                for j in range(0, len(str_name)):
                    add_coordinates(str_name[j], street_coordinates[i], c)
            else:
                add_coordinates(str_name, street_coordinates[i], c)


def add_coordinates(street, coord, c):
    if not street or street == 'nan':
        return
    if Street.objects.filter(name=street, city_site=c).exists():
        s = Street.objects.get(name=street, city_site=c)
    else:
        s = Street.objects.create(name=street, city_site=c)

    d = json.loads(gp.GeoSeries(coord).to_json())
    if d.get('features'):
        for segment in d.get('features'):
            Segment.objects.create(street=s, path=segment.get('geometry').get('coordinates'))
