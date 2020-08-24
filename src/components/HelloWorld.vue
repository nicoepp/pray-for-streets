<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-stepper v-model="step">
          <v-stepper-header>
            <v-stepper-step step="st">Choose Street</v-stepper-step>
            <v-stepper-step step="m">Map</v-stepper-step>
            <v-stepper-step step="cf">Contact Form</v-stepper-step>
          </v-stepper-header>

          <v-stepper-items>
            <v-stepper-content step="st">
              <v-card class="elevation-12">
                <v-card-text>
                  <v-form v-if="step === 'st'">
                    <v-autocomplete
                      outlined
                      label="Street"
                      name="street"
                      prepend-icon="mdi-map-search"
                      :item-text="it => it[0]"
                      :items="streets"
                      @input="selected = $event"
                    ></v-autocomplete>
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn :disabled="!selected" @click="step = 'm'" color="primary">
                    Choose
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-content step="m">
              <v-card class="elevation-12">
                <adopt-map v-if="step === 'm'" :street-name="selected"></adopt-map>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn @click="step = 'cf'" color="primary">Next</v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-content step="cf">
              <v-card class="elevation-12">
                <v-card-text>
                  <v-form>
                    <v-card-subtitle>
                      Excellent! Please fill out some contact details..
                    </v-card-subtitle>
                    <v-text-field disabled :value="selected" label="Street" outlined>
                    </v-text-field>
                    <v-text-field label="First Name" outlined></v-text-field>
                    <v-text-field label="Last Name" outlined></v-text-field>
                    <v-text-field label="Email Address" outlined></v-text-field>
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn @click="goBack">Back</v-btn>
                  <v-btn color="primary">Submit</v-btn>
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
import AdoptMap from '@/components/AdoptMap.vue';

/* Use:
*  Autocomplete component
*  https://vuetifyjs.com/en/components/autocompletes/
*
*  Abbotsford Road data:
*  https://opendata-abbotsford.hub.arcgis.com/datasets/roads/geoservice
*  https://maps.abbotsford.ca/arcgis/rest/services/GeocortexExt/WebMap/MapServer/194/query?where=STREET_NAME%20%3D%20%270%20AVE%27&outFields=OBJECTID,STREET_NAME,FROM_STREET,TO_STREET&returnGeometry=false&outSR=4326&f=json
*  https://mol.rbwm.gov.uk/mol/map/#zoom=8&lat=51.47718&lon=-0.62927
*  https://github.com/triedeti/Leaflet.streetlabels
*  https://www.twilio.com/blog/2017/08/geospatial-analysis-python-geojson-geopandas.html
*/

export default {
  name: 'HelloWorld',
  components: { AdoptMap },
  data: () => ({
    streets: [],
    selected: '',
    step: 'st',
  }),
  methods: {
    goBack() {
      this.selected = '';
      this.step = 'st';
    },
  },
  async created() {
    try {
      const resp = await axios.get('/data/just_streets.json');
      this.streets = resp.data;
    } catch (e) { console.log(); }
  },
};
</script>
