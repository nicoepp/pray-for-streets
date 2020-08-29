
def segments_to_geojson(segments, street_name=None):
    features = []
    for segment in segments:
        features.append({
            'id': segment['pk'],
            'type': "Feature",
            'properties': {
                'STREET_NAME': street_name if street_name else segment['street__name']
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': segment['path'] if segment['path'] else []
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }
