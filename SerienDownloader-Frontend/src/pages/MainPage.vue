<template>
  <v-app-bar dark fixed class="mx-0" :density="this.$vuetify.display.mobile ? 'compact' : 'default'" color="background"
             :elevation="this.$vuetify.display.mobile ? 0 : 2">
    <v-spacer/>
    <v-text-field v-if="this.$vuetify.display.mobile" label="Search..." hide-details prepend-inner-icon="mdi-magnify"
                  v-model="searchModel" class="w-66" density="compact" rounded variant="solo"
                  single-line></v-text-field>
    <v-text-field v-if="!this.$vuetify.display.mobile" label="Search..." hide-details prepend-inner-icon="mdi-magnify"
                  v-model="searchModel" rounded variant="solo" single-line></v-text-field>
    <v-spacer/>
    <v-select v-if="!this.$vuetify.display.mobile" :items="streamProvider" v-model="streamProviderSelected" hide-details
              style="position: absolute; width: auto; right: 20px;" density="compact" rounded
              variant="outlined" item-title="title" item-value="id" @update:modelValue="getStreamList"></v-select>
  </v-app-bar>
  <v-app-bar v-if="this.$vuetify.display.mobile" dark class="mx-0" density="compact" color="background" absolute>
    <v-select v-if="this.$vuetify.display.mobile" :items="streamProvider" v-model="streamProviderSelected" hide-details
              style="width: fit-content; position: absolute; right: 12%"
              density="compact" rounded
              variant="outlined" item-title="title" item-value="id" @update:modelValue="getStreamList"></v-select>
  </v-app-bar>
  <v-container>
    <v-row style="">
      <v-col class="justify-center align-center d-flex">
        <v-card :class="{'w-100': this.$vuetify.display.mobile, 'w-75': !this.$vuetify.display.mobile}"
                class="w-75 h-100 rounded-xl">
          <v-card-title class="text-center" style="font-size: 2em">Stream List</v-card-title>
          <v-divider/>
          <v-card-actions>
            <v-row>
              <v-col v-for="k in filteredAnimeList()" :key="k" class="d-flex justify-center">
                <anime-component :title="k.text" :img="k.img" :steam-provider="streamProviderSelected"></anime-component>
              </v-col>
            </v-row>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
  <v-dialog v-model="loading" max-width="500px" persistent>
    <v-card>
      <v-card-title class="text-center" style="font-size: 2em">Streaming list is loading...</v-card-title>
      <v-card-item class="d-flex justify-center">
        <v-progress-circular indeterminate :size="128"></v-progress-circular>
      </v-card-item>
      <v-spacer style="margin-top: 20px"/>
    </v-card>
  </v-dialog>
</template>

<script>
import AnimeComponent from "@/components/AnimeComponent.vue";
import axios from "axios";

const apiUrl = import.meta.env.VITE_APP_API_URL;

export default {
  name: "MainPage",
  components: {AnimeComponent},
  methods: {
    filteredAnimeList() {
      const results = this.animeList.filter(anime =>
        anime.searchParm.toLowerCase().includes(this.searchModel.toLowerCase()) || anime.text.toLowerCase().includes(this.searchModel.toLowerCase())
      );

      return results.slice(0, 100);
    },
    getStreamList() {
      this.loading = true
      axios.get(`${apiUrl}/streamList?streamProvider=${this.streamProviderSelected}`)
        .then(response => {
          this.animeList = response.data
          this.loading = false
        });
    }
  },
  async created() {
    await axios.get(`${apiUrl}/getStreamProvider`)
      .then(response => {
        this.streamProvider = response.data
        this.streamProviderSelected = 0
      })
    this.getStreamList()
  },
  data() {
    return {
      searchModel: '',
      animeList: [],
      streamProvider: [],
      streamProviderSelected: null,
      loading: true,
    }
  }
}
</script>

<style scoped>

</style>
