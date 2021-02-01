from django.core.management.base import BaseCommand, CommandError
import geopandas as gpd
import json
import osmnx as ox
from backend.streetsignup.models import Street, Segment


class Command(BaseCommand):
    help = 'Populates the Street and Segment models from the "City of Abbotsford\'s Open Data" Roads dataset'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['filename']:
            return
        place = "City of Langley, British Columbia"
        filename = options['filename'][0]
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
            s = Street.objects.create(name=street)

            df2 = streets[streets.name == street]
            d = json.loads(df2.to_json())
            if d.get('features'):
                for segment in d.get('features'):
                    Segment.objects.create(street=s, path=segment.get('geometry').get('coordinates'))
                    osmid=+1