<template>
  <div class="prayer-map"></div>
</template>

<script>
import mapboxgl from 'mapbox-gl';
import axios from 'axios';

export default {
  name: 'AdoptMap',
  props: ['streetName'],
  data() {
    return {
      map: {},
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
        zoom: 12,
      });
      this.map = map;
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

      if (this.streets?.features?.length) {
        this.fitBounds();
      }

      map.on('click', 'streets', (e) => {
        const prop = e.features[0].properties;

        new mapboxgl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`<b>${prop.STREET_NAME}</b> <br> ${prop.FROM_STREET} - ${prop.TO_STREET}`)
          .addTo(map);
      });

      map.on('mouseenter', 'streets', () => {
        map.getCanvas().style.cursor = 'pointer';
      });

      // Change it back to a pointer when it leaves.
      map.on('mouseleave', 'streets', () => {
        map.getCanvas().style.cursor = '';
      });

      // map.addControl(new mapboxgl.NavigationControl());
      // map.addControl(new mapboxgl.FullscreenControl());
    },
    fitBounds() {
      const firstCoords = this.streets.features[0].geometry.coordinates[0];
      // eslint-disable-next-line arrow-body-style
      const bounds = this.streets.features.reduce((bounds1, feat) => {
        return feat.geometry.coordinates.reduce(
          (bounds2, coord) => bounds2.extend(coord),
          bounds1,
        );
      }, new mapboxgl.LngLatBounds(firstCoords, firstCoords));

      this.map.fitBounds(bounds, { padding: 20 });
    },
    async getStreetData(name) {
      if (!name) return;
      let street = name.toLowerCase();
      street = street.replace(' ', '_').replace(' ', '_');
      street = street.replace('/', '_');
      const resp = await axios.get(`/data/streets/${street}.geo.json`);
      this.streets = resp.data;
    },
  },
  watch: {
    async streetName(name) {
      try {
        await this.getStreetData(name);
        this.map.getSource('streets').setData(this.streets);
        if (this.streets?.features?.length) {
          this.fitBounds();
        }
      } catch (e) { console.log(e.message); }
    },
  },
  async created() {
    try {
      await this.getStreetData(this.streetName);
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
