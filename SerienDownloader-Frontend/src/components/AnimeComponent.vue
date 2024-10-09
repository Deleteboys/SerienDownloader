<template>
  <!--  <v-card style="background-color: rgba(var(&#45;&#45;v-theme-secondary), .1); height: auto" width="300px" max-width="90%" class="animecomponent" @click="$router.push({ path: '/anime/'+title })">-->
  <!--    <v-card-text class="text-center d-flex align-center justify-center" style="height: 100%">-->
  <!--      {{ title.trim() }}-->
  <!--    </v-card-text>-->
  <!--  </v-card>-->
  <v-card v-if="!this.$vuetify.display.mobile"
          style="background-color: rgba(var(--v-theme-secondary), .1); border-radius: 15px" height="300px" width="180px"
          class="d-flex flex-column animecomponent"
          @click="$router.push({ path: `/anime/${title}`, query: {streamProvider:steamProvider}})">
    <v-card-item>
      <v-img :src="img" width="auto" height="200px" cover>
        <template v-slot:placeholder>
          <div class="d-flex align-center justify-center fill-height">
            <v-progress-circular
              color="grey-lighten-4"
              indeterminate
            ></v-progress-circular>
          </div>
        </template>
      </v-img>
    </v-card-item>
    <v-card-text class="text-center overflow-hidden">
      {{ title.trim() }}
    </v-card-text>
  </v-card>
  <v-card v-if="this.$vuetify.display.mobile"
          style="background-color: rgba(var(--v-theme-secondary), .1); border-radius: 15px" height="250px" width="150px"
          class="d-flex flex-column animecomponent" @click="$router.push({ path: `/anime/${title}`, query: {streamProvider:steamProvider} })">
    <v-card-item>
      <v-img :src="img" width="auto" height="150px" cover>
        <template v-slot:placeholder>
          <div class="d-flex align-center justify-center fill-height">
            <v-progress-circular
              color="grey-lighten-4"
              indeterminate
            ></v-progress-circular>
          </div>
        </template>
      </v-img>
    </v-card-item>
    <v-card-text class="text-center overflow-hidden" style="font-size: 12px">
      {{ title.trim() }}
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'AnimeComponent',
  props: {
    title: String,
    img: String,
    steamProvider: Number
  }
}
</script>

<style scoped>
.animecomponent {
  transition: transform .1s ease-in-out;
}

.animecomponent:hover {
  transform: scale(1.05)
}
</style>
