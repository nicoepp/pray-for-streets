import Vue from 'vue';
import App from './App.vue';
import vuetify from './plugins/vuetify';

Vue.config.productionTip = false;

new Vue({
  vuetify,
  render: (h) => h(App),
}).$mount('#app');

// eslint-disable-next-line prefer-destructuring
// window.pfs = app.$children[0].$children[0].$children[1].$children[0];
