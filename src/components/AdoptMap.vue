<template>
  <div class="prayer-map"></div>
</template>

<script>
import mapboxgl from 'mapbox-gl';
import axios from 'axios';

export default {
  name: 'AdoptMap',
  data() {
    return {
      streets: [],
    };
  },
  methods: {
    initMap() {
      mapboxgl.accessToken = 'pk.eyJ1Ijoibmljb2VwcCIsImEiOiJja2U1eXA5ZHYxN3Q1MzBwOGVnemN1a2l5In0.l7OoW5D-wjPsMimVIMnXFA';
      const map = new mapboxgl.Map({
        container: this.$el,
        style: 'mapbox://styles/mapbox/light-v10',
        center: [-122.36109, 49.06213],
        zoom: 15,
      });
      map.on('load', () => {
        map.addSource('streets', {
          type: 'geojson',
          data: this.streets,
        });
        map.addLayer({
          id: 'streets',
          type: 'line',
          source: 'streets',
          paint: { 'line-width': 2 },
        });
      });
    },
  },
  async created() {
    try {
      const resp = await axios.get('/data/streets.geo.json');
      this.streets = resp.data;
    } catch (e) { console.log(e.message); }
    this.initMap();
  },
};
</script>

<style scoped>
  .prayer-map {
    height: 450px;
    width: 100%;
  }
</style>
