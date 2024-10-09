<template>
  <v-navigation-drawer
    expand-on-hover
    rail
    color="background"
  >
    <v-list>
      <v-list-item
      ></v-list-item>
    </v-list>

    <v-list density="compact" nav>
      <v-list-item prepend-icon="mdi-home" :to="'/'" link title="Home" value="home"></v-list-item>
      <v-list-item prepend-icon="mdi-download" :to="'/download'" link title="Download" value="download"></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>

</script>

<style scoped>

</style>
