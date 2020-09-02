import Vue from 'vue';
import Vuetify from 'vuetify/lib';
import colors from 'vuetify/lib/util/colors';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: colors.grey.darken4,
        secondary: colors.grey.darken2,
        accent: colors.grey.darken4,
        error: colors.red.darken2,
      },
    },
  },
});
