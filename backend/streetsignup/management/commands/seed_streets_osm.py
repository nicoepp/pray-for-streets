from django.core.management.base import BaseCommand
import json
import osmnx as ox
from backend.streetsignup.models import Street, Segment, City


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
        st = set()
        for street in street_names:
            if not street or street == 'nan':
                continue
            if isinstance(street, list):
                for str in street:
                    st.add(str)
                continue
            st.add(street)
        if City.objects.filter(name=city_db).exists():
            c = City.objects.get(name=city_db)
        else:
            c = City.objects.create(name=city_db, province=province_name, site='not necessary')
        for street in st:
            if not street or street == 'nan':
                continue
            if Street.objects.filter(name=street, city_site=c).exists():
                s = Street.objects.get(name=street, city_site=c)
            else:
                s = Street.objects.create(name=street, city_site=c)

            df2 = streets[streets.name == street]
            d = json.loads(df2.to_json())
            if d.get('features'):
                for segment in d.get('features'):
                    Segment.objects.create(street=s, path=segment.get('geometry').get('coordinates'))
