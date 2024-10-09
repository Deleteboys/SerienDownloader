<template>
  <v-container class="fill-height" fluid>
    <v-responsive class="d-flex justify-center align-center fill-height">
      <v-row>
        <v-col class="justify-center align-center d-flex">
          <v-card :class="{'w-100': this.$vuetify.display.mobile, 'w-50': !this.$vuetify.display.mobile}"
                  class="rounded-xl">
            <v-card-title class="text-center" style="font-size: 2em">Download Options</v-card-title>
            <v-divider/>
            <v-card-actions>
              <v-row>
                <v-col class="d-flex flex-column align-center">
                  <v-card-title style="font-size: 1.5em" class="text-wrap text-center">{{
                      animeName
                    }}
                  </v-card-title>
                  <v-switch label="Download hole season" disabled
                            :class="{'w-100': this.$vuetify.display.mobile, 'w-50': !this.$vuetify.display.mobile}"
                            v-model="downloadSeason"/>
                  <v-switch label="Download german only" disabled
                            :class="{'w-100': this.$vuetify.display.mobile, 'w-50': !this.$vuetify.display.mobile}"
                            v-model="downloadGermanOnly"/>
                  <v-select label="Select Season"
                            v-model="selectedSeason"
                            :class="{'w-100': this.$vuetify.display.mobile, 'w-50': !this.$vuetify.display.mobile}"
                            :items="seasonArray"></v-select>
                  <v-select label="Select Episode"
                            :class="{'w-100': this.$vuetify.display.mobile, 'w-50': !this.$vuetify.display.mobile}"
                            v-if="!downloadSeason" :items="episodeArray"></v-select>
                  <v-btn :class="{'w-50': this.$vuetify.display.mobile, 'w-25': !this.$vuetify.display.mobile}"
                         color="primary" @click="downloadAnime">Download
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-responsive>
  </v-container>
</template>


<script>
import axios from "axios";

const apiUrl = import.meta.env.VITE_APP_API_URL;

export default {
  name: "AnimeDownloadPage",
  data() {
    return {
      animeName: "Loading...",
      downloadSeason: true,
      downloadGermanOnly: false,
      seasonRaw: [],
      seasonArray: [],
      streamProvider: null,
      selectedSeason: "",
      pictureUrl: "",
      episodeArray: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30'],
    }
  },
  created() {
    this.animeName = this.$route.params.name;
    this.streamProvider = this.$route.query.streamProvider;
    const data = {
      "series_name": this.animeName,
      "streamProvider": this.streamProvider
    }
    axios.post(`${apiUrl}/getSeasonsFromSeries`, data).then(response => {
      this.seasonRaw = response.data
      this.seasonArray = this.seasonRaw.map(i => i.text)
    })
    // axios.get("https://api.jikan.moe/v4/anime?q=" + this.animeName).then(response => {
    //   this.pictureUrl = response.data.data[0].images.webp.image_url
    // })
  },
  methods: {
    downloadAnime() {
      var link = this.seasonRaw.filter(i => i.text === this.selectedSeason)[0].href
      if (link !== null) {
        const data = {
          "series": this.animeName,
          "season_link": link,
          "season": this.selectedSeason,
          "streamProvider": this.streamProvider
        }
        axios.post(`${apiUrl}/downloadSeries`, data).then(() => {
          this.$router.push({path: '/download'})
        }).catch(() => {
          alert("ERROR")
        })
      } else {
        alert("Select a season")
      }
    }
  }

}
</script>

<style scoped>

</style>
