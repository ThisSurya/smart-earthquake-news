import { createRouter, createWebHistory } from 'vue-router'
import EarthquakeView from '../views/EarthquakeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'earthquake',
      component: EarthquakeView,
    },
  ],
})

export default router
