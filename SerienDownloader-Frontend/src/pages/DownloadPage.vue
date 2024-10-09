<template>
  <v-container class="fill-height" fluid>
    <v-responsive class="d-flex justify-center align-center fill-height">
      <v-row class="justify-center align-center d-flex">
        <v-col cols="12" md="10">
          <v-card class="w-100 rounded-xl">
            <v-card-title class="text-center" style="font-size: 2em">Current Download</v-card-title>
            <v-divider/>
            <v-card-actions>
              <v-row class="d-flex align-center" v-if="animeTitle.length !== 0">
                <v-col cols="12" md="12">
                  <v-card-title class="text-center text-wrap" style="font-size: 1.5em">{{ animeTitle }}</v-card-title>
                  <v-card-text class="text-center text-wrap" style="font-size: 1.1em">Season {{ season }} Episode {{ episode }}
                  </v-card-text>
<!--                                    <v-progress-linear indeterminate-->
<!--                                                       :class="{'w-100': this.$vuetify.display.mobile, 'w-66': !this.$vuetify.display.mobile}"-->
<!--                                                       height="20px" color="primary">-->
<!--                                    </v-progress-linear>-->
                  <v-progress-linear v-model="downloadPercentage"
                                     :class="{'w-100': this.$vuetify.display.mobile, 'w-66': !this.$vuetify.display.mobile}"
                                     height="20px" color="primary">
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}%</strong>
                    </template>
                  </v-progress-linear>
                </v-col>
                <v-col class="text-center text-wrap">
                  <v-card-text style="font-size: 1.2em">Download time: {{ downloadTime }}</v-card-text>
                </v-col>
                <v-col class="text-center text-wrap">
                  <v-card-text style="font-size: 1.2em">Speed: {{ downloadSpeed }}</v-card-text>
                </v-col>
              </v-row>
              <v-row class="d-flex align-center" v-if="animeTitle.length === 0">
                <v-col cols="12" md="12">
                  <v-card-title class="text-center text-wrap" style="font-size: 1.5em">Currently there is no download</v-card-title>
                </v-col>
              </v-row>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="12" md="5">
          <v-card class="w-100 rounded-xl" height="550px">
            <v-card-title class="text-center" style="font-size: 2em">Download Queue</v-card-title>
            <v-divider/>
            <v-card-actions>
              <v-container class="d-flex flex-column justify-center align-center rounded-xl"
                           style="overflow-y: scroll; height: 485px; background: rgba(var(--v-theme-background), 1)">
                <v-row class="w-100 h-100">
                  <v-col v-for="i in downloadQueue" :key="i" cols="12" md="12">
                    <v-card>
                      <v-row>
                        <v-col class="d-flex align-center">
                          <v-card-text class="text-center" style="max-width: 40%">{{ i.series }}</v-card-text>
                          <v-card-text class="text-center" style="max-width: 40%">Season {{ i.season }}</v-card-text>
                          <v-card-text class="text-center" style="max-width: 40%">Episode {{ i.episode }}</v-card-text>
                        </v-col>
                      </v-row>
                    </v-card>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-actions>
          </v-card>
        </v-col>
<!--        <v-col cols="12" md="5">-->
<!--          <v-card class="w-100 rounded-xl" height="500px">-->
<!--            <v-card-title class="text-center" style="font-size: 2em">Download History</v-card-title>-->
<!--            <v-divider/>-->
<!--            <v-card-actions>-->
<!--              <v-container class="d-flex flex-column justify-center align-center rounded-xl"-->
<!--                           style="overflow-y: scroll; height: 435px; background: rgba(var(&#45;&#45;v-theme-background), 1)">-->
<!--                <v-row class="w-100 h-100">-->
<!--                  <v-col v-for="i in 100" :key="i" cols="12" md="12">-->
<!--                    <v-card>-->
<!--                      <v-row>-->
<!--                        <v-col class="d-flex align-center">-->
<!--                          <v-card-text class="text-center" style="max-width: 40%">Sword art Online</v-card-text>-->
<!--                          <v-card-text class="text-center" style="max-width: 40%">Season 1</v-card-text>-->
<!--                          <v-card-text class="text-center" style="max-width: 40%">Episode {{ i }}</v-card-text>-->
<!--                        </v-col>-->
<!--                      </v-row>-->
<!--                    </v-card>-->
<!--                  </v-col>-->
<!--                </v-row>-->
<!--              </v-container>-->
<!--            </v-card-actions>-->
<!--          </v-card>-->
<!--        </v-col>-->
        <v-col cols="12" md="5">
          <v-card class="w-100 rounded-xl" height="550px">
            <v-card-title class="text-center" style="font-size: 2em">Failed Downloads</v-card-title>
            <v-divider/>
            <v-card-actions>
              <v-container class="d-flex flex-column justify-center align-center rounded-xl flex-column"
                           style="overflow-y: scroll; height: 435px; background: rgba(var(--v-theme-background), 1)">
                <v-row class="w-100 h-100">
                  <v-col v-for="i in failedDownloads" :key="i" cols="12" md="12">
                    <v-card>
                      <v-row>
                        <v-col class="d-flex align-center">
                          <v-card-text class="text-center" style="max-width: 40%">{{ i.series }}</v-card-text>
                          <v-card-text class="text-center" style="max-width: 40%">Season {{ i.season }}</v-card-text>
                          <v-card-text class="text-center" style="max-width: 40%">Episode {{ i.episode }}</v-card-text>
                        </v-col>
                      </v-row>
                    </v-card>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-actions>
            <v-card-actions class="d-flex justify-center">
              <v-btn color="primary" @click="retryFailed_downloads">Retry failed Downloads</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-responsive>
  </v-container>
</template>

<script>
import {io} from "socket.io-client";
import axios from "axios";

const wsUrl = import.meta.env.VITE_APP_WS_URL;
const apiUrl = import.meta.env.VITE_APP_API_URL;

export default {
  name: "DownloadPage",

  data() {
    return {
      downloadPercentage: 0,
      downloadSpeed: "",
      downloadTime: "",
      animeTitle: "",
      season: "",
      episode: "",
      downloadQueue: [],
      failedDownloads: [],
    }
  },
  methods: {
    updateAnimeList() {
      axios.get(`${apiUrl}/getAllQueueSeries`)
        .then(response => {
          this.downloadQueue = response.data
        });
    },
    updateFailedDownloads() {
      axios.get(`${apiUrl}/failedDownloads`)
        .then(response => {
          this.failedDownloads = response.data
        });
    },
    retryFailed_downloads() {
      axios.get(`${apiUrl}/retryFailedDownloadSeries`);
    }
  },
  mounted() {
    const socket = io(wsUrl);

    this.updateAnimeList();
    this.updateFailedDownloads();

    socket.on("connect", () => {
      console.log("connected")
    });
    socket.on("broadcast_message", data => {
      if (data.percentage !== undefined) {
        this.downloadPercentage = data.percentage
        this.downloadSpeed = data.download_speed
        this.downloadTime = data.estimated_time
        this.animeTitle = data.animeTitle
        this.season = data.season
        this.episode = data.episode
      }
      if (data.update !== undefined) {
        this.updateAnimeList();
        this.updateFailedDownloads();
      }
    });
  }
}
</script>

<style scoped>

</style>
