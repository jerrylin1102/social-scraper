<template>
  <div class="space-y-6 animate-fade-in pb-12">
    <!-- Header Controls -->
    <div class="flex items-center justify-between sticky top-16 z-30 bg-white/80 backdrop-blur-md py-3 -mx-4 px-4 sm:mx-0 sm:px-0 sm:bg-transparent sm:backdrop-blur-none sm:py-0 border-b border-slate-100 sm:border-none">
      <button class="btn-ghost -ml-2 text-slate-700 hover:text-black transition-colors" @click="router.push({ name: 'home' })">
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="font-medium">返回首頁</span>
      </button>

      <div v-if="entry" class="flex items-center gap-1">
        <button class="btn-ghost text-slate-500 hover:text-black hover:bg-slate-100" :disabled="store.loading" @click="refresh" title="重新整理">
          <svg class="h-5 w-5" :class="{'animate-spin': store.loading}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 0 0 4.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 0 1-15.357-2m15.357 2H15" />
          </svg>
        </button>
        <button class="btn-ghost text-red-400 hover:text-red-600 hover:bg-red-50" @click="removeCurrent" title="移除紀錄">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <section v-if="!entry" class="card px-6 py-16 text-center shadow-sm border-slate-100">
      <div class="mx-auto w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
        <svg class="h-8 w-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="text-lg font-semibold text-slate-800">找不到這份報告了！</p>
      <p class="mt-2 text-sm text-slate-500 max-w-sm mx-auto">可能已經被刪除，或是你在其他裝置上看的！</p>
      <button class="btn-primary mt-6 px-8 rounded-full" @click="router.push({ name: 'home' })">回到首頁去探索</button>
    </section>

    <template v-else>
      <div class="grid gap-6 lg:gap-8 xl:grid-cols-[340px_minmax(0,1fr)] items-start">

        <!-- Left Sidebar: Profile Identity -->
        <aside class="space-y-6">
          <!-- Profile Card -->
          <div class="bg-white rounded-[32px] p-8 shadow-sm border border-slate-100 relative overflow-hidden group">
            <div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 opacity-80 z-0"></div>

            <div class="relative z-10 flex flex-col items-center">
              <div class="relative">
                <div class="mx-auto flex h-28 w-28 items-center justify-center overflow-hidden rounded-full bg-white ring-[4px] ring-white shadow-md z-10 relative">
                  <img
                    v-if="avatar"
                    :src="avatar"
                    :alt="entry.username"
                    class="h-full w-full object-cover"
                  />
                  <span v-else class="text-3xl font-bold bg-gradient-to-br from-slate-800 to-slate-600 bg-clip-text text-transparent">
                    {{ entry.username?.[0]?.toUpperCase() }}
                  </span>
                </div>
                <div class="absolute -bottom-2 -right-2 bg-white rounded-full p-1 shadow-sm z-20 flex gap-1">
                  <span
                    v-for="platform in entry.requested_platforms"
                    :key="platform"
                    :class="platformBadgeClass(platform)"
                    class="!scale-90"
                  >
                    {{ platformLabel(platform) }}
                  </span>
                </div>
              </div>

              <div class="mt-6 text-center w-full">
                <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 truncate px-2">
                  {{ displayName }}
                </h1>
                <p class="mt-1 text-sm font-medium text-slate-500">@{{ entry.username }}</p>

                <div class="mt-4 inline-block bg-slate-50 rounded-2xl px-4 py-2.5 text-sm font-medium leading-relaxed text-slate-700 border border-slate-100 w-full">
                  {{ entry.analysis.personality.headline }}
                </div>
              </div>

              <div class="mt-6 w-full text-left">
                <p class="text-[11px] font-bold uppercase tracking-widest text-slate-400 mb-2">公開簡介</p>
                <p class="text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">
                  {{ profileBio || '沒有寫簡介也沒關係，AI 還是能從發文裡感覺出他的個性喔！' }}
                </p>
              </div>
            </div>
          </div>

          <!-- MBTI Card -->
          <div class="rounded-[32px] bg-gradient-to-br from-slate-900 to-slate-800 p-8 text-white shadow-lg shadow-slate-900/10 relative overflow-hidden">
            <div class="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-3xl"></div>
            <div class="absolute -bottom-10 -left-10 w-40 h-40 bg-indigo-500/20 rounded-full blur-3xl"></div>

            <div class="relative z-10">
              <div class="flex justify-between items-center">
                <p class="text-[11px] font-bold uppercase tracking-[0.2em] text-white/50">MBTI 人格分析</p>
                <span class="px-2.5 py-1 rounded-full bg-white/10 text-[10px] font-medium backdrop-blur-sm border border-white/5">
                  {{ mbtiStrength }}
                </span>
              </div>
              <div class="mt-5">
                <p class="text-5xl font-black tracking-widest bg-gradient-to-r from-white via-indigo-100 to-white bg-clip-text text-transparent">
                  {{ entry.analysis.mbti.type }}
                </p>
              </div>
              <p class="mt-5 text-sm leading-relaxed text-white/80 font-medium">
                {{ entry.analysis.mbti.reason }}
              </p>
            </div>
          </div>

          <!-- Basic Info Card -->
          <div class="rounded-[32px] bg-white p-8 shadow-sm border border-slate-100">
            <div class="flex items-center justify-between mb-6">
              <p class="text-sm font-bold text-slate-900">AI 推測小檔案</p>
              <span class="text-[10px] font-medium text-slate-400 bg-slate-50 px-2 py-1 rounded-full">
                {{ formatDate(entry.analyzed_at, { dateStyle: 'short' }) }} 分析
              </span>
            </div>

            <div v-if="visibleFacts.length" class="space-y-4">
              <div v-for="fact in visibleFacts" :key="fact.key" class="group">
                <div class="flex items-baseline justify-between gap-4">
                  <p class="text-sm font-medium text-slate-500">{{ fact.label }}</p>
                  <p class="text-right text-sm font-bold text-slate-800">{{ fact.value }}</p>
                </div>
                <p v-if="fact.evidence" class="mt-1.5 text-xs leading-relaxed text-slate-400 bg-slate-50 rounded-xl p-2.5 hidden group-hover:block transition-all">
                  <span class="font-medium text-slate-500 mr-1">🔍 線索：</span>{{ fact.evidence }}
                </p>
              </div>
            </div>

            <p v-else class="text-sm leading-relaxed text-slate-400 text-center py-4 bg-slate-50 rounded-2xl">
              目前貼文裡還沒有透露太多年齡、學校或生日的秘密呢。
            </p>
          </div>
        </aside>

        <!-- Right Content: Deep Analysis -->
        <div class="space-y-6 lg:space-y-8">

          <!-- Personality Impression -->
          <div class="rounded-[32px] bg-white p-8 sm:p-10 shadow-sm border border-slate-100 bg-gradient-to-br from-white to-slate-50/50">
            <p class="text-[11px] font-bold uppercase tracking-widest text-indigo-500 mb-4 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              AI 人物印象
            </p>
            <p class="text-xl sm:text-2xl font-bold leading-relaxed text-slate-800">
              {{ entry.analysis.personality.summary }}
            </p>

            <div class="mt-8 flex flex-wrap gap-2.5">
              <span v-for="trait in traits" :key="trait" class="px-4 py-2 rounded-full bg-indigo-50 text-indigo-700 text-sm font-semibold border border-indigo-100 shadow-sm">
                {{ trait }}
              </span>
            </div>
          </div>

          <div class="grid gap-6 lg:gap-8 lg:grid-cols-2">
            <!-- Interests -->
            <section class="rounded-[32px] bg-white p-8 shadow-sm border border-slate-100">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 rounded-full bg-pink-50 flex items-center justify-center text-pink-500">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <div>
                  <h2 class="text-lg font-bold text-slate-900">興趣偏好</h2>
                  <p class="text-xs font-medium text-slate-400">{{ interests.length ? `${interests.length} 個重點` : '尚在整理中' }}</p>
                </div>
              </div>

              <div v-if="interests.length" class="space-y-3">
                <div
                  v-for="(interest, index) in interests"
                  :key="`${interest}-${index}`"
                  class="group flex items-start gap-3 rounded-2xl bg-slate-50/80 px-4 py-3.5 hover:bg-pink-50 transition-colors"
                >
                  <span class="text-pink-400 mt-0.5">•</span>
                  <p class="text-sm font-medium leading-relaxed text-slate-700 group-hover:text-slate-900">
                    {{ interest }}
                  </p>
                </div>
              </div>

              <div v-else class="flex flex-col items-center justify-center py-8 px-4 text-center bg-slate-50 rounded-3xl">
                <p class="text-sm font-medium text-slate-400">平常發文比較隨性，還沒看出特別著迷的興趣！</p>
              </div>
            </section>

            <!-- Chat Topics -->
            <section class="rounded-[32px] bg-white p-8 shadow-sm border border-slate-100">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-500">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <div>
                  <h2 class="text-lg font-bold text-slate-900">話題建議</h2>
                  <p class="text-xs font-medium text-slate-400">{{ chatTopics.length ? `${chatTopics.length} 個方向` : '尚在整理中' }}</p>
                </div>
              </div>

              <div v-if="chatTopics.length" class="space-y-3">
                <div
                  v-for="(topic, index) in chatTopics"
                  :key="`${topic}-${index}`"
                  class="rounded-2xl border border-slate-100 bg-white px-4 py-3.5 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] hover:border-blue-200 transition-colors relative pl-10"
                >
                  <span class="absolute left-4 top-4 text-blue-400">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                    </svg>
                  </span>
                  <p class="text-sm font-medium leading-relaxed text-slate-700">
                    {{ topic }}
                  </p>
                </div>
              </div>

              <div v-else class="flex flex-col items-center justify-center py-8 px-4 text-center bg-slate-50 rounded-3xl">
                <p class="text-sm font-medium text-slate-400">暫時沒看出特別的興趣，可以直接從最近的動態關心喔！</p>
              </div>
            </section>
          </div>

          <!-- Key Events -->
          <section class="rounded-[32px] bg-white p-8 sm:p-10 shadow-sm border border-slate-100">
            <div class="flex items-center gap-3 mb-8">
              <div class="w-10 h-10 rounded-full bg-amber-50 flex items-center justify-center text-amber-500">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h2 class="text-xl font-bold text-slate-900">近期重要經歷</h2>
                <p class="text-sm font-medium text-slate-400">{{ keyEvents.length ? `捕捉到 ${keyEvents.length} 個精彩時刻` : '尚在整理中' }}</p>
              </div>
            </div>

            <div v-if="keyEvents.length" class="space-y-0 relative">
              <!-- Timeline line -->
              <div class="absolute left-[19px] top-4 bottom-4 w-[2px] bg-slate-100"></div>

              <div
                v-for="(event, index) in keyEvents"
                :key="`${event}-${index}`"
                class="relative flex gap-6 pb-6 last:pb-0"
              >
                <!-- Timeline dot -->
                <div class="relative z-10 flex flex-col items-center pt-2">
                  <div class="h-10 w-10 rounded-full bg-white border-4 border-amber-100 flex items-center justify-center shadow-sm">
                    <span class="h-3 w-3 rounded-full bg-amber-400"></span>
                  </div>
                </div>

                <div class="flex-1 rounded-3xl bg-slate-50 px-6 py-5 hover:bg-amber-50/50 transition-colors border border-transparent hover:border-amber-100">
                  <p class="text-[15px] font-medium leading-relaxed text-slate-700">{{ event }}</p>
                </div>
              </div>
            </div>

            <div v-else class="flex flex-col items-center justify-center py-10 px-4 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-200">
              <svg class="w-8 h-8 text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm font-medium text-slate-500">最近好像沒有特別分享哪裡玩或發生的大事呢！</p>
            </div>
          </section>

          <!-- Fallback/Error state -->
          <section
            v-if="entry.failed_platforms.length"
            class="rounded-[24px] border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 px-6 py-5 text-sm font-medium leading-relaxed text-amber-800 shadow-sm flex items-start gap-3"
          >
            <svg class="w-5 h-5 text-amber-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              哎呀！這次有些平台的貼文沒辦法順利讀取，所以內容可能比較短。可以等一下再<button @click="refresh" class="underline underline-offset-2 hover:text-amber-600 font-bold mx-1">重新整理</button>試試看！
            </div>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
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

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const store = useScraperStore()

const entry = computed(() => store.getAnalysis(props.id))
const primarySource = computed(() => getPrimarySource(entry.value?.results || []))
const avatar = computed(() => getAvatar(primarySource.value?.profile))
const displayName = computed(() => getDisplayName(entry.value?.results || [], entry.value?.username || ''))
const profileBio = computed(() => primarySource.value?.profile?.bio || '')

function cleanList(items) {
  return Array.isArray(items)
    ? items.map(item => `${item || ''}`.trim()).filter(Boolean)
    : []
}

const traits = computed(() => cleanList(entry.value?.analysis?.personality?.traits))
const interests = computed(() => cleanList(entry.value?.analysis?.interests))
const chatTopics = computed(() => cleanList(entry.value?.analysis?.chat_topics))
const keyEvents = computed(() => cleanList(entry.value?.analysis?.key_events))

const visibleFacts = computed(() => {
  if (!entry.value) return []
  const facts = entry.value.analysis.inferred_facts
  const labels = {
    age: '年齡',
    birthday: '生日',
    height: '身高',
    location: '居住地',
    school_or_company: '學校 / 公司',
    zodiac: '星座',
  }

  return Object.entries(labels)
    .map(([key, label]) => {
      const fact = facts[key]
      if (!fact?.value) return null
      return {
        key,
        label,
        value: key === 'age' && !`${fact.value}`.includes('歲') ? `${fact.value} 歲` : fact.value,
        evidence: fact.evidence,
      }
    })
    .filter(Boolean)
})

const mbtiStrength = computed(() => {
  const confidence = entry.value?.analysis?.mbti?.confidence
  return {
    high: '很明確',
    medium: '中等',
    low: '初步推測',
  }[confidence] || '初步推測'
})

async function refresh() {
  if (!entry.value) return
  if (!window.confirm('要讓 AI 重新閱讀最新的貼文，並更新這份報告嗎？')) return
  try {
    const refreshed = await store.refreshAnalysis(entry.value.id)
    router.replace({ name: 'analysis', params: { id: refreshed.id } })
  } catch {
    // Error state is already handled in the store.
  }
}

function removeCurrent() {
  if (!entry.value) return
  if (!window.confirm('確定要刪除這份報告嗎？')) return
  store.deleteAnalysis(entry.value.id)
  router.push({ name: 'home' })
}
</script>
