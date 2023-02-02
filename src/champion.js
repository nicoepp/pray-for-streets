import Vue from 'vue';
import ChampionMap from '@/components/ChampionMap.vue';
import vuetify from '@/plugins/vuetify';

Vue.config.productionTip = false;

new Vue({
  vuetify,
  render: (h) => h(ChampionMap),
}).$mount('#app');
