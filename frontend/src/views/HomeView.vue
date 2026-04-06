<template>
  <div class="space-y-8 animate-fade-in">
    <section class="card overflow-hidden relative border-0 shadow-md">
      <!-- Decorative backgrounds -->
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-pink-400/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl"></div>

      <div class="bg-white/60 backdrop-blur-xl px-6 py-10 sm:px-12 sm:py-16 relative z-10">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/80 border border-slate-100 shadow-sm mb-6">
          <span class="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
          <p class="text-[11px] font-bold uppercase tracking-widest text-slate-500">AI Social Analysis</p>
        </div>

        <h1 class="max-w-3xl text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl leading-[1.15]">
          快速了解你自己，<br class="hidden sm:block" />
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">或是秒懂新朋友！</span>
        </h1>
        <p class="mt-6 max-w-2xl text-sm leading-relaxed text-slate-600 sm:text-base font-medium">
          輸入 Instagram 或 Threads 帳號，AI 會自動閱讀他的貼文與簡介，為你找出個性、興趣、近期亮點、MBTI 甚至推薦聊天話題！
        </p>

        <form class="mt-10 relative z-20" @submit.prevent="submit">
          <div class="card border-0 bg-white p-3 shadow-xl shadow-indigo-100/50 ring-1 ring-slate-100">
            <div class="flex flex-col gap-3 lg:flex-row">
              <div class="flex flex-1 items-center rounded-2xl border border-slate-100 bg-slate-50/50 px-4 focus-within:bg-white focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
                <span class="text-slate-400 font-medium mr-1">@</span>
                <input
                  v-model="username"
                  type="text"
                  placeholder="username、IG/Threads 連結"
                  class="w-full bg-transparent px-2 py-4 text-base font-medium text-slate-900 outline-none placeholder:text-slate-400 placeholder:font-normal"
                />
              </div>

              <button class="btn-primary h-[58px] justify-center px-8 text-base rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 hover:from-slate-800 hover:to-slate-700 shadow-md shadow-slate-900/20" :disabled="store.loading || !username.trim()">
                <svg v-if="store.loading" class="h-5 w-5 animate-spin mr-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v8H4z" />
                </svg>
                <span class="font-bold">{{ store.loading ? '分析中…' : '開始分析' }}</span>
              </button>
            </div>

            <div class="mt-4 flex justify-center px-1">
              <div class="inline-flex w-full sm:w-auto rounded-[16px] bg-slate-50/80 p-1.5 border border-slate-100/50 backdrop-blur-sm shadow-inner">
                <button
                  v-for="option in platformOptions"
                  :key="option.value"
                  type="button"
                  class="platform-pill flex-1 sm:flex-none sm:px-8 rounded-xl py-2.5 text-sm font-bold transition-all duration-300"
                  :class="selectedPlatform === option.value ? option.activeClass : 'text-slate-500 hover:text-slate-700 hover:bg-white/60'"
                  @click="selectedPlatform = option.value"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>
          </div>
        </form>

        <p v-if="store.error" class="mt-6 rounded-2xl bg-red-50 border border-red-100 px-5 py-4 text-sm font-medium text-red-600 flex items-start gap-3 shadow-sm">
          <svg class="w-5 h-5 text-red-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{{ store.error }}</span>
        </p>
      </div>
    </section>

    <section v-if="store.loading" class="card p-6 sm:p-7 border-indigo-100 bg-indigo-50/50">
      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-sm font-bold text-slate-900">正在為你解讀 @{{ cleanedPreview }} ...</p>
          <p class="mt-1.5 text-sm text-slate-500 font-medium">AI 正在努力閱讀貼文與整理線索，大約需要 20 到 90 秒，請稍微等一下下哦！</p>
        </div>
        <div class="grid gap-2.5 text-sm text-indigo-700 font-medium">
          <div class="chip-soft border-indigo-200 bg-white">1. 閱讀公開主頁 👀</div>
          <div class="chip-soft border-indigo-200 bg-white">2. 消化貼文內容 🧠</div>
          <div class="chip-soft border-indigo-200 bg-white">3. 產生專屬分析 ✨</div>
        </div>
      </div>
    </section>

    <section class="space-y-4">
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-slate-900">你看過誰？</h2>
          <p class="text-sm font-medium text-slate-500">幫你記住了最近看過的 {{ store.recentAnalyses.length }} 個靈魂</p>
        </div>
        <button
          v-if="store.recentAnalyses.length"
          class="btn-ghost text-sm"
          @click="clearAnalyses"
        >
          清空紀錄
        </button>
      </div>

      <div v-if="store.recentAnalyses.length" class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <article
          v-for="item in store.recentAnalyses"
          :key="item.id"
          class="card group cursor-pointer p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
          @click="openAnalysis(item.id)"
        >
          <div class="flex items-start gap-4">
            <div class="flex h-14 w-14 items-center justify-center overflow-hidden rounded-full bg-slate-100 ring-2 ring-slate-100">
              <img
                v-if="getAvatar(primarySource(item)?.profile)"
                :src="getAvatar(primarySource(item)?.profile)"
                :alt="item.username"
                class="h-full w-full object-cover"
              />
              <span v-else class="text-lg font-semibold text-slate-400">
                {{ item.username?.[0]?.toUpperCase() }}
              </span>
            </div>

            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <p class="truncate font-semibold text-slate-900">
                  {{ getDisplayName(item.results, item.username) }}
                </p>
                <span
                  v-for="platform in item.requested_platforms"
                  :key="`${item.id}-${platform}`"
                  :class="platformBadgeClass(platform)"
                >
                  {{ platformLabel(platform) }}
                </span>
              </div>
              <p class="mt-1 text-sm text-slate-400">@{{ item.username }}</p>
              <p class="mt-3 text-sm font-medium text-slate-700">
                {{ item.analysis.personality.headline }}
              </p>
              <p class="mt-1 line-clamp-2 text-sm leading-6 text-slate-500">
                {{ item.analysis.personality.summary }}
              </p>
            </div>

            <button
              class="rounded-xl p-2 text-slate-300 transition-colors hover:bg-red-50 hover:text-red-400"
              @click.stop="removeAnalysis(item.id)"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0 1 16.138 21H7.862a2 2 0 0 1-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          <div class="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-4 text-xs text-slate-400">
            <span class="chip">{{ item.analysis.mbti.type }}</span>
            <span
              v-for="interest in item.analysis.interests.slice(0, 3)"
              :key="`${item.id}-${interest}`"
              class="chip-soft"
            >
              {{ interest }}
            </span>
            <span class="ml-auto">{{ formatDate(item.analyzed_at, { dateStyle: 'short', timeStyle: 'short' }) }}</span>
          </div>
        </article>
      </div>

      <div v-else class="card flex flex-col items-center justify-center px-6 py-16 text-center border-dashed border-slate-200 bg-slate-50/50">
        <div class="flex h-14 w-14 items-center justify-center rounded-full bg-white shadow-sm border border-slate-100">
          <svg class="h-7 w-7 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12h18M12 3v18" />
          </svg>
        </div>
        <p class="mt-4 text-base font-bold text-slate-700">還沒看過任何人嗎？</p>
        <p class="mt-2 max-w-md text-sm leading-6 text-slate-500 font-medium">
          趕快在上方輸入朋友或你的帳號試試看！<br class="hidden sm:block" />支援 IG 或 Threads，也可以一起看！
        </p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useScraperStore } from '@/stores/scraper'
import {
  formatDate,
  getAvatar,
  getDisplayName,
  getPrimarySource,
  platformBadgeClass,
  platformLabel,
} from '@/utils/analysis'

const router = useRouter()
const store = useScraperStore()

const username = ref('')
const selectedPlatform = ref('both')

const platformOptions = [
  { value: 'threads', label: '只看 Threads', activeClass: 'bg-black text-white shadow-sm' },
  { value: 'instagram', label: '只看 Instagram', activeClass: 'bg-slate-900 text-white shadow-sm' },
  { value: 'both', label: '一起分析', activeClass: 'bg-white text-slate-900 shadow-sm' },
]

const selectedPlatforms = computed(() =>
  selectedPlatform.value === 'both' ? ['threads', 'instagram'] : [selectedPlatform.value]
)

const cleanedPreview = computed(() => username.value.trim().replace(/^@/, '') || 'username')

function primarySource(item) {
  return getPrimarySource(item?.results || [])
}

async function submit() {
  if (!username.value.trim() || store.loading) return
  try {
    const entry = await store.analyze(username.value.trim(), selectedPlatforms.value)
    username.value = ''
    router.push({ name: 'analysis', params: { id: entry.id } })
  } catch {
    // Error state is already handled in the store.
  }
}

function openAnalysis(id) {
  router.push({ name: 'analysis', params: { id } })
}

function removeAnalysis(id) {
  if (!window.confirm('要刪除這份報告嗎？')) return
  store.deleteAnalysis(id)
}

function clearAnalyses() {
  if (!window.confirm('確定要清空所有的歷史紀錄嗎？')) return
  store.clearAnalyses()
}
</script>
