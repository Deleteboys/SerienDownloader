/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import {createRouter, createWebHistory} from 'vue-router'
import MainPage from "@/pages/MainPage.vue";
import AnimeDownloadPage from "@/pages/AnimeDownloadPage.vue";
import DownloadPage from "@/pages/DownloadPage.vue";

const routes = [
  {path: '/', component: MainPage, meta: { requiresAuth: true }},
  {path: '/anime/:name', component: AnimeDownloadPage, meta: { requiresAuth: true }},
  {path: '/download', component: DownloadPage, meta: { requiresAuth: true }},
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
