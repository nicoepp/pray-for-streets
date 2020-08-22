<template>
 <l-map :zoom="zoom" :center="center" style="height: 500px; width: 100%">
  <l-tile-layer :url="url" :attribution="attribution"></l-tile-layer>
   <l-polygon :lat-lngs="polygon.latlngs" :color="polygon.color"></l-polygon>
   <l-geo-json :geojson="streets"></l-geo-json>
 </l-map>
</template>

<script>
import L from 'leaflet';
import {
  LMap, LTileLayer, LPolygon, LGeoJson,
} from 'vue2-leaflet';
import axios from 'axios';

export default {
  name: 'AdoptMap',
  components: {
    LMap, LTileLayer, LPolygon, LGeoJson,
  },
  data() {
    return {
      zoom: 16,
      center: L.latLng(49.06212598820834, -122.36109312981736),
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', // Replace 'c' with '{s}'
      attribution:
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      polygon: {
        latlngs: [
          [49.0621259882, -122.36309312981736],
          [49.0651259882, -122.36307888507733], // GeoJSON is longLat
          [49.0651259882, -122.36488424187341],
          [49.0621259882, -122.36309312981736],
        ],
        color: '#ff00ff',
      },
      streets: [],
    };
  },
  async created() {
    try {
      const resp = await axios.get('/data/streets.geo.json');
      this.streets = resp.data;
    } catch (e) { console.log(); }
  },
};
</script>

<style scoped>

</style>
