<template>
  <v-app>
    <v-main>
      <border-component v-if="!this.$vuetify.display.mobile"/>
      <v-bottom-navigation v-if="this.$vuetify.display.mobile" v-model="value">
        <v-btn :to="'/'" value="home" width="40%">
          <v-icon>mdi-home</v-icon>
          <span>Home</span>
        </v-btn>

        <v-btn :to="'/download'" value="download" width="40%">
          <v-icon>mdi-download</v-icon>

          <span>Download</span>
        </v-btn>
      </v-bottom-navigation>
      <router-view/>
    </v-main>
  </v-app>
</template>

<script>

import BorderComponent from "@/components/BorderComponent.vue";

export default {
  name: "App",
  components: {BorderComponent},
  data() {
    return {
      value: 0,
    }
  },
}
</script>
