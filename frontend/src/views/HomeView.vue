<template>
  <div class="space-y-8 animate-fade-in">
    <section class="card overflow-hidden">
      <div class="bg-gradient-to-br from-white via-slate-50 to-slate-100 px-6 py-8 sm:px-10 sm:py-12">
        <p class="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">AI Social Analysis</p>
        <h1 class="mt-3 max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          用公開社群資料，快速看懂一個人
        </h1>
        <p class="mt-4 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
          輸入 Instagram 或 Threads 帳號，先抓公開資料與貼文，再交給 AI 整理出個性、興趣、重要經歷、MBTI 與適合聊天的切入點。
        </p>

        <form class="mt-8" @submit.prevent="submit">
          <div class="card border-slate-200 bg-white/95 p-3 shadow-lg shadow-slate-200/60">
            <div class="flex flex-col gap-3 lg:flex-row">
              <div class="flex flex-1 items-center rounded-2xl border border-slate-200 bg-slate-50 px-4">
                <svg class="h-5 w-5 flex-shrink-0 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Z" />
                </svg>
                <input
                  v-model="username"
                  type="text"
                  placeholder="@username、IG/Threads 個人頁連結"
                  class="w-full bg-transparent px-3 py-4 text-base text-slate-900 outline-none placeholder:text-slate-400"
                />
              </div>

              <button class="btn-primary h-[58px] justify-center px-7 text-base" :disabled="store.loading || !username.trim()">
                <svg v-if="store.loading" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v8H4z" />
                </svg>
                {{ store.loading ? '分析中…' : '開始分析' }}
              </button>
            </div>

            <div class="mt-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div class="inline-flex w-full rounded-full bg-slate-100 p-1 lg:w-auto">
                <button
                  v-for="option in platformOptions"
                  :key="option.value"
                  type="button"
                  class="platform-pill flex-1"
                  :class="selectedPlatform === option.value ? option.activeClass : 'text-slate-500 hover:text-slate-700'"
                  @click="selectedPlatform = option.value"
                >
                  {{ option.label }}
                </button>
              </div>

              <p class="text-xs text-slate-400">
                分析結果只會保存在這台裝置的 `localStorage`，不會寫入後端資料庫。
              </p>
            </div>
          </div>
        </form>

        <p v-if="store.error" class="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-500">
          {{ store.error }}
        </p>
      </div>
    </section>

    <section v-if="store.loading" class="card p-6 sm:p-7">
      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-sm font-semibold text-slate-900">正在分析 @{{ cleanedPreview }}</p>
          <p class="mt-1 text-sm text-slate-500">流程會先爬取公開資料，再交給 AI 做整理與推測，通常需要 20 到 90 秒。</p>
        </div>
        <div class="grid gap-2 text-sm text-slate-500">
          <div class="chip-soft">1. 抓取公開個人資料</div>
          <div class="chip-soft">2. 整理貼文文字與線索</div>
          <div class="chip-soft">3. 產出 AI 分析結果</div>
        </div>
      </div>
    </section>

    <section class="space-y-4">
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">最近分析</h2>
          <p class="text-sm text-slate-400">保留最近 {{ store.recentAnalyses.length }} 筆本機紀錄。</p>
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

      <div v-else class="card flex flex-col items-center justify-center px-6 py-16 text-center">
        <div class="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100">
          <svg class="h-7 w-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12h18M12 3v18" />
          </svg>
        </div>
        <p class="mt-4 text-base font-medium text-slate-700">還沒有分析紀錄</p>
        <p class="mt-2 max-w-md text-sm leading-6 text-slate-400">
          上方直接輸入帳號即可開始。支援只分析 Threads、只分析 Instagram，或兩個平台一起分析。
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
  if (!window.confirm('要從這台裝置移除這筆分析紀錄嗎？')) return
  store.deleteAnalysis(id)
}

function clearAnalyses() {
  if (!window.confirm('要清空目前瀏覽器中的所有分析紀錄嗎？')) return
  store.clearAnalyses()
}
</script>
