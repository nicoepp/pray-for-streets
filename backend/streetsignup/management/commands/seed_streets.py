from django.core.management.base import BaseCommand, CommandError
import geopandas as gpd
import json
from backend.streetsignup.models import Street, Segment


class Command(BaseCommand):
    help = 'Populates the Street and Segment models from the "City of Abbotsford\'s Open Data" Roads dataset'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['filename']:
            return
        filename = options['filename'][0]
        df = gpd.read_file(filename)

        df = df[['OBJECTID', 'STREET_NAME', 'geometry']]
        street_names = df['STREET_NAME'].unique().tolist()

        for street in street_names:
            if not street or street == 'N/A':
                continue
            st = Street.objects.create(name=street)

            df2 = df[df['STREET_NAME'] == street]
            d = json.loads(df2.to_json())

            for segment in d['features']:
                Segment.objects.create(street=st,
                                       objectid=segment['properties']['OBJECTID'],
                                       path=segment['geometry']['coordinates'])
