<template>
  <adopt-map controls="true" style="height: 600px" :street-geo-json="covered_streets"></adopt-map>
</template>

<script>
import AdoptMap from '@/components/AdoptMap.vue';
import axios from 'axios';

export default {
  name: 'CoverageMap',
  components: { AdoptMap },
  data: () => ({
    covered_streets: {
      type: 'FeatureCollection',
      features: [],
    },
  }),
  methods: {
    isAllStreets() {
      const urlParams = new URLSearchParams(window.top.location.search);
      return urlParams.get('all_streets') === '';
    },
  },
  async created() {
    try {
      const url = window.location.hostname;
      let resp;
      if (this.isAllStreets()) {
        resp = await axios.get(`/api/streets/all_streets.geo.json?site=${url}`);
      } else {
        resp = await axios.get(`/api/streets/covered_streets.geo.json?site=${url}`);
      }
      this.covered_streets = resp.data;
    } catch (e) { console.log(); }
  },
};
</script>
