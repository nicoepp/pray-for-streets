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
  async created() {
    try {
      const resp = await axios.get('/api/streets/covered_streets.geo.json');
      this.covered_streets = resp.data;
    } catch (e) { console.log(); }
  },
};
</script>
