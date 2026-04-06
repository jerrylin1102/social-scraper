<template>
  <div class="animate-fade-in">
    <!-- Back -->
    <button class="btn-ghost mb-6 -ml-2" @click="router.back()">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      返回
    </button>

    <!-- Loading -->
    <div v-if="loading" class="space-y-4">
      <div class="card p-6 animate-pulse flex gap-4">
        <div class="w-20 h-20 rounded-full bg-slate-200 shrink-0"/>
        <div class="flex-1 space-y-3">
          <div class="h-5 bg-slate-200 rounded w-1/3"/>
          <div class="h-4 bg-slate-200 rounded w-1/4"/>
          <div class="h-3 bg-slate-200 rounded w-2/3"/>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="card p-8 text-center">
      <p class="text-red-500 font-medium">{{ error }}</p>
      <button class="btn-primary mt-4" @click="load">重新載入</button>
    </div>

    <!-- Content -->
    <template v-else-if="profile">
      <!-- Profile header -->
      <div class="card p-6 mb-6">
        <div class="flex flex-col sm:flex-row gap-5">
          <!-- Avatar -->
          <div class="shrink-0">
            <img v-if="profile.profile_pic_local" :src="profile.profile_pic_local"
                 :alt="profile.username"
                 class="w-24 h-24 rounded-full object-cover ring-2 ring-slate-100" />
            <div v-else class="w-24 h-24 rounded-full bg-slate-200 flex items-center justify-center text-3xl font-bold text-slate-400">
              {{ profile.username[0]?.toUpperCase() }}
            </div>
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <h2 class="text-xl font-bold text-slate-900 truncate">{{ profile.full_name || profile.username }}</h2>
              <span v-if="profile.is_verified" title="已驗證" class="text-blue-500">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </span>
              <span :class="profile.platform === 'threads' ? 'badge-threads' : 'badge-instagram'">
                {{ profile.platform === 'threads' ? 'Threads' : 'Instagram' }}
              </span>
            </div>
            <p class="text-slate-500 text-sm mb-3">@{{ profile.username }}</p>
            <p v-if="profile.bio" class="text-slate-700 text-sm whitespace-pre-wrap mb-3">{{ profile.bio }}</p>
            <a v-if="profile.website" :href="profile.website" target="_blank"
               class="text-sm text-blue-600 hover:underline break-all">{{ profile.website }}</a>

            <!-- Stats -->
            <div class="flex gap-6 mt-4">
              <div class="text-center">
                <p class="font-bold text-slate-900 text-lg">{{ fmt(profile.followers_count) }}</p>
                <p class="text-xs text-slate-500">追蹤者</p>
              </div>
              <div class="text-center">
                <p class="font-bold text-slate-900 text-lg">{{ fmt(profile.following_count) }}</p>
                <p class="text-xs text-slate-500">追蹤中</p>
              </div>
              <div class="text-center">
                <p class="font-bold text-slate-900 text-lg">{{ fmt(profile.total_posts) }}</p>
                <p class="text-xs text-slate-500">貼文</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Scrape info -->
        <div class="mt-4 pt-4 border-t border-slate-100 flex justify-between items-center text-xs text-slate-400">
          <span>上次爬取：{{ fmtDate(profile.scraped_at) }}</span>
          <button class="btn-ghost text-xs py-1 px-3" @click="refresh">重新爬取</button>
        </div>
      </div>

      <!-- Posts -->
      <div class="mb-4 flex items-center justify-between">
        <h3 class="font-semibold text-slate-800">貼文列表
          <span class="text-slate-400 font-normal text-sm ml-1">({{ profile.total_posts }} 篇)</span>
        </h3>
        <input v-model="search" placeholder="搜尋貼文…"
               class="text-sm px-3 py-1.5 rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 w-48" />
      </div>
      <PostList :posts="filteredPosts" :platform="profile.platform" />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useScraperStore } from '@/stores/scraper'
import PostList from '@/components/PostList.vue'

const props  = defineProps({ platform: String, username: String })
const router = useRouter()
const store  = useScraperStore()

const profile = ref(null)
const loading = ref(true)
const error   = ref(null)
const search  = ref('')

async function load() {
  loading.value = true; error.value = null
  try { profile.value = await store.getProfile(props.platform, props.username) }
  catch (e) { error.value = e.response?.data?.detail || '載入失敗' }
  finally { loading.value = false }
}

async function refresh() {
  if (!confirm('重新爬取將更新全部資料，確定繼續？')) return
  try {
    const res = await store.scrape(props.platform, props.username)
    profile.value = res.profile
  } catch (e) { alert(e.message) }
}

const filteredPosts = computed(() => {
  if (!profile.value?.posts) return []
  if (!search.value.trim()) return profile.value.posts
  const q = search.value.toLowerCase()
  return profile.value.posts.filter(p => p.text?.toLowerCase().includes(q))
})

const fmt = n => n >= 1_000_000 ? (n / 1_000_000).toFixed(1) + 'M'
               : n >= 1_000     ? (n / 1_000).toFixed(1) + 'K' : (n ?? 0).toString()
const fmtDate = d => d ? new Date(d).toLocaleString('zh-TW') : ''

onMounted(load)
</script>
