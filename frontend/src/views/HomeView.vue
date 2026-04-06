<template>
  <div class="animate-fade-in">
    <!-- Hero -->
    <div class="mb-10 text-center">
      <h1 class="text-3xl font-bold text-slate-900 mb-2">Social Scraper</h1>
      <p class="text-slate-500 text-sm">爬取公開 Threads 與 Instagram 帳號的資料與貼文</p>
    </div>

    <!-- Action bar -->
    <div class="flex items-center justify-between mb-6">
      <p class="text-sm text-slate-500">
        共 <span class="font-semibold text-slate-800">{{ store.profiles.length }}</span> 個已爬取帳號
      </p>
      <button class="btn-primary" @click="showModal = true">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        新增爬取
      </button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="initLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="card p-5 animate-pulse">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-14 h-14 rounded-full bg-slate-200"/>
          <div class="flex-1 space-y-2">
            <div class="h-4 bg-slate-200 rounded w-3/4"/>
            <div class="h-3 bg-slate-200 rounded w-1/2"/>
          </div>
        </div>
        <div class="h-3 bg-slate-200 rounded w-full mb-2"/>
        <div class="h-3 bg-slate-200 rounded w-2/3"/>
      </div>
    </div>

    <!-- Profile grid -->
    <div v-else-if="store.profiles.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <ProfileCard
        v-for="p in store.profiles" :key="`${p.platform}-${p.username}`"
        :profile="p"
        @click="goToProfile(p)"
        @delete="confirmDelete(p)"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-24 text-center">
      <div class="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0"/>
        </svg>
      </div>
      <p class="text-slate-600 font-medium mb-1">尚未爬取任何帳號</p>
      <p class="text-slate-400 text-sm mb-4">點擊「新增爬取」開始爬取公開帳號</p>
      <button class="btn-primary" @click="showModal = true">立即新增</button>
    </div>

    <!-- Scrape Modal -->
    <ScrapeModal v-if="showModal" @close="showModal = false" @done="onDone" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useScraperStore } from '@/stores/scraper'
import ProfileCard from '@/components/ProfileCard.vue'
import ScrapeModal from '@/components/ScrapeModal.vue'

const store      = useScraperStore()
const router     = useRouter()
const showModal  = ref(false)
const initLoading = ref(true)

onMounted(async () => {
  await store.fetchProfiles()
  initLoading.value = false
})

function goToProfile(p) {
  router.push({ name: 'profile', params: { platform: p.platform, username: p.username } })
}

async function confirmDelete(p) {
  if (!confirm(`確定要刪除 @${p.username} 的所有資料嗎？`)) return
  await store.deleteProfile(p.platform, p.username)
}

function onDone(result) {
  showModal.value = false
  if (result?.profile) goToProfile(result.profile)
}
</script>
