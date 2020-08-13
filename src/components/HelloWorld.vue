<template>
  <v-container
        class="fill-height"
        fluid
      >
        <v-row
          align="center"
          justify="center"
        >
          <v-col
            cols="12"
            sm="8"
            md="4"
          >
            <v-card class="elevation-12">
              <v-toolbar
                color="primary"
                dark
                flat
              >
                <v-toolbar-title>Select a street</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-icon>mdi-code-tags</v-icon>
              </v-toolbar>
              <v-card-text>
                <v-form>
                  <v-autocomplete
                    outlined
                    label="Street"
                    name="street"
                    prepend-icon="mdi-map-search"
                    :item-text="it => it[0]"
                    :items="[
                     ['McCallum Rd'], ['Marshall Rd'], ['Maclure Rd'], ['McKenzie Rd'], ['James St']
                    ]"
                    @input="inputLog"
                  ></v-autocomplete>
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary">Choose</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
</template>

<script>
/* Use:
*  Autocomplete component
*  https://vuetifyjs.com/en/components/autocompletes/
*
*  Abbotsford Road data:
*  https://opendata-abbotsford.hub.arcgis.com/datasets/roads/geoservice
*  https://maps.abbotsford.ca/arcgis/rest/services/GeocortexExt/WebMap/MapServer/194/query?where=STREET_NAME%20%3D%20%270%20AVE%27&outFields=OBJECTID,STREET_NAME,FROM_STREET,TO_STREET&returnGeometry=false&outSR=4326&f=json
*  https://mol.rbwm.gov.uk/mol/map/#zoom=8&lat=51.47718&lon=-0.62927
*  https://github.com/triedeti/Leaflet.streetlabels
*/

export default {
  name: 'HelloWorld',

  data: () => ({
  }),
  methods: {
    inputLog(ev) {
      console.log(ev);
    },
  },
};
</script>
