from django.core.management.base import BaseCommand, CommandError
import geopandas as gpd
import json
import osmnx as ox
from backend.streetsignup.models import Street, Segment


class Command(BaseCommand):
    help = 'Populates the Street and Segment models fetching data from OpenStreetMaps'

    def add_arguments(self, parser):
        parser.add_argument('place', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['place']:
            return
        # place = "City of Langley, British Columbia"
        place = options['place'][0]
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

        osmid = 0
        for street in st:
            if not street or street == 'nan':
                continue
            if Street.object.filter(name=street).exists():
                s = Street.objects.get(name=street)
            else:
                s = Street.objects.create(name=street)

            df2 = streets[streets.name == street]
            d = json.loads(df2.to_json())
            if d.get('features'):
                for segment in d.get('features'):
                    Segment.objects.create(street=s, path=segment.get('geometry').get('coordinates'))
                    osmid=+1
