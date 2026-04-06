import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import AnalysisView from '@/views/AnalysisView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView, name: 'home' },
    {
      path: '/analysis/:id',
      component: AnalysisView,
      props: true,
      name: 'analysis',
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
