<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <button class="btn-ghost -ml-2" @click="router.push({ name: 'home' })">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回首頁
      </button>

      <div v-if="entry" class="flex flex-wrap gap-2">
        <button class="btn-ghost" :disabled="store.loading" @click="refresh">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 0 0 4.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 0 1-15.357-2m15.357 2H15" />
          </svg>
          {{ store.loading ? '重新整理中…' : '重新整理' }}
        </button>
        <button class="btn-ghost text-red-500 hover:bg-red-50" @click="removeCurrent">
          移除紀錄
        </button>
      </div>
    </div>

    <section v-if="!entry" class="card px-6 py-12 text-center">
      <p class="text-base font-medium text-slate-700">找不到這頁內容</p>
      <p class="mt-2 text-sm text-slate-400">這筆整理可能已被移除，或目前這台裝置沒有保存它。</p>
      <button class="btn-primary mt-5" @click="router.push({ name: 'home' })">回到首頁</button>
    </section>

    <template v-else>
      <section class="card overflow-hidden">
        <div class="bg-gradient-to-br from-white via-slate-50 to-slate-100 px-6 py-8 sm:px-8 sm:py-10">
          <div class="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
            <aside class="space-y-4">
              <div class="rounded-[28px] bg-white p-6 shadow-sm">
                <div class="mx-auto flex h-28 w-28 items-center justify-center overflow-hidden rounded-full bg-slate-100 ring-4 ring-slate-100">
                  <img
                    v-if="avatar"
                    :src="avatar"
                    :alt="entry.username"
                    class="h-full w-full object-cover"
                  />
                  <span v-else class="text-3xl font-semibold text-slate-400">
                    {{ entry.username?.[0]?.toUpperCase() }}
                  </span>
                </div>

                <div class="mt-5 text-center">
                  <h1 class="text-2xl font-bold tracking-tight text-slate-900">
                    {{ displayName }}
                  </h1>
                  <p class="mt-1 text-sm text-slate-400">@{{ entry.username }}</p>
                  <p class="mt-4 text-sm leading-7 text-slate-600">
                    {{ entry.analysis.personality.headline }}
                  </p>
                </div>

                <div class="mt-5 flex flex-wrap justify-center gap-2">
                  <span
                    v-for="platform in entry.requested_platforms"
                    :key="platform"
                    :class="platformBadgeClass(platform)"
                  >
                    {{ platformLabel(platform) }}
                  </span>
                </div>

                <div class="mt-6 border-t border-slate-100 pt-5">
                  <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">簡介</p>
                  <p class="mt-3 text-sm leading-7 text-slate-600">
                    {{ profileBio || '目前沒有留下公開自介，以下內容以整體貼文風格與生活線索為主。' }}
                  </p>
                </div>
              </div>

              <div class="rounded-[28px] bg-slate-900 px-6 py-6 text-white shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-white/50">MBTI 參考</p>
                <div class="mt-4">
                  <p class="text-4xl font-bold tracking-[0.16em] sm:text-5xl">
                    {{ entry.analysis.mbti.type }}
                  </p>
                  <p class="mt-3 text-sm text-white/70">判斷強度：{{ mbtiStrength }}</p>
                </div>
                <p class="mt-5 text-sm leading-7 text-white/80">
                  {{ entry.analysis.mbti.reason }}
                </p>
              </div>

              <div class="rounded-[28px] bg-white p-6 shadow-sm">
                <div class="flex items-center justify-between gap-3">
                  <p class="text-sm font-semibold text-slate-900">個人資訊</p>
                  <span class="text-xs text-slate-400">更新於 {{ formatDate(entry.analyzed_at, { dateStyle: 'short', timeStyle: 'short' }) }}</span>
                </div>

                <div v-if="visibleFacts.length" class="mt-4 space-y-4">
                  <div v-for="fact in visibleFacts" :key="fact.key" class="border-b border-slate-100 pb-4 last:border-b-0 last:pb-0">
                    <div class="flex items-start justify-between gap-4">
                      <p class="text-sm text-slate-400">{{ fact.label }}</p>
                      <p class="text-right text-sm font-medium text-slate-900">{{ fact.value }}</p>
                    </div>
                    <p v-if="fact.evidence" class="mt-2 text-xs leading-5 text-slate-400">{{ fact.evidence }}</p>
                  </div>
                </div>

                <p v-else class="mt-4 text-sm leading-7 text-slate-400">
                  目前還沒有足夠線索可以整理出年齡、生日或學校等個人資訊。
                </p>
              </div>
            </aside>

            <div class="space-y-4">
              <div class="rounded-[32px] bg-white px-6 py-7 shadow-sm sm:px-8">
                <p class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">人物印象</p>
                <p class="mt-4 text-lg font-semibold leading-8 text-slate-900 sm:text-2xl sm:leading-10">
                  {{ entry.analysis.personality.summary }}
                </p>

                <div class="mt-6 flex flex-wrap gap-2">
                  <span v-for="trait in traits" :key="trait" class="chip-soft">
                    {{ trait }}
                  </span>
                </div>
              </div>

              <div class="grid gap-4 lg:grid-cols-2">
                <section class="card p-6 sm:p-7">
                  <div class="flex items-center justify-between gap-3">
                    <h2 class="text-lg font-semibold text-slate-900">興趣偏好</h2>
                    <span class="text-xs text-slate-400">{{ interests.length ? `${interests.length} 個重點` : '尚在整理中' }}</span>
                  </div>

                  <div v-if="interests.length" class="mt-5 space-y-3">
                    <div
                      v-for="(interest, index) in interests"
                      :key="`${interest}-${index}`"
                      class="rounded-2xl bg-slate-50 px-4 py-3"
                    >
                      <p class="text-sm font-medium leading-6 text-slate-700">
                        {{ interest }}
                      </p>
                    </div>
                  </div>

                  <p v-else class="mt-5 text-sm leading-7 text-slate-400">
                    這次內容裡還看不出特別穩定的興趣主軸。
                  </p>
                </section>

                <section class="card p-6 sm:p-7">
                  <div class="flex items-center justify-between gap-3">
                    <h2 class="text-lg font-semibold text-slate-900">聊天切入點</h2>
                    <span class="text-xs text-slate-400">{{ chatTopics.length ? `${chatTopics.length} 個方向` : '尚在整理中' }}</span>
                  </div>

                  <div v-if="chatTopics.length" class="mt-5 space-y-3">
                    <div
                      v-for="(topic, index) in chatTopics"
                      :key="`${topic}-${index}`"
                      class="rounded-2xl border border-slate-100 bg-white px-4 py-3 shadow-sm"
                    >
                      <p class="text-sm leading-6 text-slate-700">
                        {{ topic }}
                      </p>
                    </div>
                  </div>

                  <p v-else class="mt-5 text-sm leading-7 text-slate-400">
                    目前還沒有整理出特別適合直接開聊的主題。
                  </p>
                </section>
              </div>

              <section class="card p-6 sm:p-7">
                <div class="flex items-center justify-between gap-3">
                  <h2 class="text-lg font-semibold text-slate-900">近期重要經歷</h2>
                  <span class="text-xs text-slate-400">{{ keyEvents.length ? `${keyEvents.length} 則` : '尚在整理中' }}</span>
                </div>

                <div v-if="keyEvents.length" class="mt-6 space-y-4">
                  <div
                    v-for="(event, index) in keyEvents"
                    :key="`${event}-${index}`"
                    class="flex gap-4"
                  >
                    <div class="flex flex-col items-center">
                      <span class="mt-1 h-2.5 w-2.5 rounded-full bg-slate-900" />
                      <span
                        v-if="index !== keyEvents.length - 1"
                        class="mt-2 block w-px flex-1 bg-slate-200"
                      />
                    </div>

                    <div class="flex-1 rounded-2xl bg-slate-50 px-4 py-3">
                      <p class="text-sm leading-7 text-slate-700">{{ event }}</p>
                    </div>
                  </div>
                </div>

                <p v-else class="mt-5 text-sm leading-7 text-slate-400">
                  暫時沒有整理出特別明確的大事件或活動紀錄。
                </p>
              </section>

              <section
                v-if="entry.failed_platforms.length"
                class="rounded-[28px] border border-amber-100 bg-amber-50 px-6 py-5 text-sm leading-7 text-amber-700"
              >
                這次能整理到的內容比較有限，所以部分欄位會較簡短，之後重新整理可能會得到更完整的結果。
              </section>
            </div>
          </div>
        </div>
      </section>
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
  if (!window.confirm('要重新抓取內容並重新整理這份頁面嗎？')) return
  try {
    const refreshed = await store.refreshAnalysis(entry.value.id)
    router.replace({ name: 'analysis', params: { id: refreshed.id } })
  } catch {
    // Error state is already handled in the store.
  }
}

function removeCurrent() {
  if (!entry.value) return
  if (!window.confirm('要從這台裝置移除這筆整理紀錄嗎？')) return
  store.deleteAnalysis(entry.value.id)
  router.push({ name: 'home' })
}
</script>
