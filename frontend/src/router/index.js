import { createRouter, createWebHistory } from 'vue-router'
import HomeView    from '@/views/HomeView.vue'
import ProfileView from '@/views/ProfileView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',                              component: HomeView },
    { path: '/:platform/:username',           component: ProfileView,
      props: true, name: 'profile' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
