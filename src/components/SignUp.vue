<template>
  <v-container fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5">
        <v-stepper v-model="step" class="elevation-6">
          <v-stepper-header>
            <v-stepper-step step="st">Choose Street</v-stepper-step>
            <v-stepper-step step="m">Map</v-stepper-step>
            <v-stepper-step step="cf">Contact Form</v-stepper-step>
          </v-stepper-header>

          <v-stepper-items>
            <v-stepper-content step="st">
              <v-card>
                <v-card-text>
                  <v-form v-if="step === 'st'">
                    <v-autocomplete
                      outlined
                      label="Street"
                      name="street"
                      prepend-icon="mdi-map-search"
                      :item-value="item => item"
                      item-text="name"
                      :items="streets"
                      @input="selected = $event"
                      :hint="warnHint"
                      :error-messages="errorHint"
                    ></v-autocomplete>
                  </v-form>
                  <adopt-map v-if="combined" :street-geo-json="covered_streets"></adopt-map>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    :disabled="!selected || selected.subs >= MAX_PER_STREET"
                    @click="step = 'm'"
                    color="primary"
                  >
                    Choose
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-content step="m">
              <v-card>
                <adopt-map v-if="step === 'm'" :street-geo-json="street_features">
                </adopt-map>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn @click="goBack">Back</v-btn>
                  <v-btn @click="step = 'cf'" color="primary">Next</v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-content step="cf">
              <v-card>
                <template v-if="submitSuccess">
                  <v-card-title>Thank you!</v-card-title>
                  <v-card-text>
                    Your subscription was succesfully submitted! You will receive an confirmation
                    Email shortly.
                  </v-card-text>
                </template>
                <v-card-text v-else>
                  <v-form v-if="step === 'cf'" v-model="validRules">
                    <v-card-subtitle v-if="!errorMessage">
                      Please fill out contact details and submit to sign up and receive a reminder.
                    </v-card-subtitle>
                    <v-card-subtitle v-else style="color: red">
                      {{ errorMessage }}
                    </v-card-subtitle>
                    <v-text-field
                      disabled :value="selected.name" label="Street" outlined
                    ></v-text-field>
                    <v-text-field
                      v-model="form.name" :rules="rules.name" label="Name" outlined
                    ></v-text-field>
                    <v-text-field
                      v-model="form.email" :rules="rules.email" label="Email Address" outlined
                      validate-on-blur
                    ></v-text-field>
                    <v-text-field
                      v-model="form.church"
                      :rules="rules.church"
                      label="Church Affiliation"
                      outlined
                    ></v-text-field>
                    <vue-recaptcha
                      @verify="form.token = $event"
                      @expired="form.token = ''"
                      :sitekey="reCaptchaKey"
                    ></vue-recaptcha>
                    <div class="pt-5">
                      Disclaimer: Your information will not be used for marketing purposes,
                      only for this event.
                    </div>
                  </v-form>
                </v-card-text>
                <v-card-actions v-if="!submitSuccess">
                  <v-spacer></v-spacer>
                  <v-btn @click="step = 'm'">Back</v-btn>
                  <v-btn @click="submit" color="primary" :disabled="!formValid">Submit</v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
          </v-stepper-items>
        </v-stepper>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';
import VueRecaptcha from 'vue-recaptcha';
import AdoptMap from '@/components/AdoptMap.vue';

/* Use:
*  Autocomplete component
*  https://vuetifyjs.com/en/components/autocompletes/
*
*  Abbotsford Road data:
*  https://opendata-abbotsford.hub.arcgis.com/datasets/roads/geoservice
*  https://mol.rbwm.gov.uk/mol/map/#zoom=8&lat=51.47718&lon=-0.62927
*  https://github.com/triedeti/Leaflet.streetlabels
*  https://www.twilio.com/blog/2017/08/geospatial-analysis-python-geojson-geopandas.html
*/

let reCaptchaKey = process.env.VUE_APP_RECAPTCHA_SITE_KEY;
reCaptchaKey = reCaptchaKey || '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI';

export default {
  name: 'HelloWorld',
  components: { AdoptMap, VueRecaptcha },
  data: () => ({
    streets: [],
    selected: null,
    street_features: {
      type: 'FeatureCollection',
      features: [],
    },
    covered_streets: {
      type: 'FeatureCollection',
      features: [],
    },
    step: 'st',
    combined: false,
    MAX_PER_STREET: 3,
    form: {
      name: '',
      email: '',
      church: '',
      token: '',
    },
    submitSuccess: false,
    errorMessage: '',
    validRules: false,
    rules: { // eslint-disable-next-line arrow-parens
      name: [val => !!val || 'Required.', val => (val || '').length <= 30 || 'Max 30 characters'],
      email: [
        (value) => !!value || 'Required.',
        (value) => {
          const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          return pattern.test(value) || 'Invalid e-mail.';
        },
      ], // eslint-disable-next-line arrow-parens
      church: [val => !!val || 'Required.', val => (val || '').length <= 40 || 'Max 40 characters'],
    },
    reCaptchaKey,
  }),
  computed: {
    formValid() {
      return this.validRules && this.form.token && this.selected?.id > 0 && this.selected?.name;
    },
    warnHint() {
      if (this.selected?.subs > 0) {
        return `There are already ${this.selected?.subs} subscriptions for this street`;
      }
      return '';
    },
    errorHint() {
      if (this.selected?.subs >= this.MAX_PER_STREET) {
        return `${this.selected?.subs} subscriptions already. Please select another street.`;
      }
      return '';
    },
  },
  methods: {
    goBack() {
      this.selected = null;
      this.step = 'st';
      this.submitSuccess = false;
    },
    async getStreetData(streetId) {
      if (!streetId) throw Error('Name is not defined');
      const resp = await axios.get(`/api/streets/${streetId}.geo.json`);
      return resp.data;
    },
    async submit() {
      if (!this.selected?.id) return;
      const form = {
        street_name: this.selected?.name || '',
        ...this.form,
      };

      try {
        const resp = await axios.post(`/api/streets/${this.selected.id}/subscribe`, form);
        if (resp.data.success) {
          this.submitSuccess = true;
          this.errorMessage = '';
          // eslint-disable-next-line no-multi-assign
          this.form.name = this.form.email = this.form.church = this.form.token = '';
        } else {
          this.errorMessage = 'Sorry, something went wrong';
          console.log(resp.data.success);
        }
      } catch (e) {
        this.errorMessage = 'Sorry, something went wrong while submitting the form';
        console.log(e.response.data);
      }
    },
  },
  watch: {
    async selected(obj) {
      if (!obj?.id) return;
      try {
        this.street_features = await this.getStreetData(obj.id);
      } catch (e) { console.log(e.message); }
    },
  },
  async created() {
    try {
      const resp = await axios.get('/api/streets');
      if (resp.data?.streets) {
        this.streets = resp.data.streets;
      }

      const resp2 = await axios.get('/api/streets/covered_streets.geo.json');
      this.covered_streets = resp2.data;
    } catch (e) { console.log(); }
  },
};
</script>
