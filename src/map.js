import Vue from 'vue';
import CoverageMap from '@/components/CoverageMap.vue';

Vue.config.productionTip = false;

new Vue({
  render: (h) => h(CoverageMap),
}).$mount('#map');
