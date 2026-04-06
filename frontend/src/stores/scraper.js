import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import axios from 'axios'
import { withBackendBase } from '@/utils/backend'
import { normalizePlatforms } from '@/utils/analysis'

const STORAGE_KEY = 'social-scraper-analyses-v1'
const HISTORY_LIMIT = 8

function loadAnalyses() {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function persistAnalyses(entries) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(entries))
}

function buildQueryKey(username, platforms) {
  return `${username.toLowerCase()}::${normalizePlatforms(platforms).sort().join('+')}`
}

function createId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `analysis-${Date.now()}`
}

export const useScraperStore = defineStore('scraper', () => {
  const analyses = ref(loadAnalyses())
  const loading = ref(false)
  const error = ref(null)

  const recentAnalyses = computed(() =>
    [...analyses.value].sort((a, b) => new Date(b.analyzed_at) - new Date(a.analyzed_at))
  )

  function upsertAnalysis(payload) {
    const platforms = normalizePlatforms(payload.requested_platforms || [])
    const queryKey = buildQueryKey(payload.username, platforms)
    const existing = analyses.value.find(item => item.queryKey === queryKey)
    const entry = {
      ...payload,
      id: existing?.id || createId(),
      queryKey,
      requested_platforms: platforms,
      completed_platforms: normalizePlatforms(payload.completed_platforms || []),
      failed_platforms: normalizePlatforms(payload.failed_platforms || []),
    }

    analyses.value = [
      entry,
      ...analyses.value.filter(item => item.queryKey !== queryKey),
    ].slice(0, HISTORY_LIMIT)
    persistAnalyses(analyses.value)
    return entry
  }

  async function analyze(username, platforms) {
    loading.value = true
    error.value = null
    try {
      const { data } = await axios.post(
        withBackendBase('/api/analyze'),
        { username, platforms: normalizePlatforms(platforms) },
        { timeout: 240_000 },
      )
      return upsertAnalysis(data)
    } catch (e) {
      const msg = e.response?.data?.detail || '分析失敗，請稍後再試。'
      error.value = msg
      throw new Error(msg)
    } finally {
      loading.value = false
    }
  }

  function getAnalysis(id) {
    return analyses.value.find(item => item.id === id) || null
  }

  async function refreshAnalysis(id) {
    const entry = getAnalysis(id)
    if (!entry) {
      throw new Error('找不到分析紀錄')
    }
    return analyze(entry.username, entry.requested_platforms)
  }

  function deleteAnalysis(id) {
    analyses.value = analyses.value.filter(item => item.id !== id)
    persistAnalyses(analyses.value)
  }

  function clearAnalyses() {
    analyses.value = []
    persistAnalyses(analyses.value)
  }

  return {
    analyses,
    recentAnalyses,
    loading,
    error,
    analyze,
    getAnalysis,
    refreshAnalysis,
    deleteAnalysis,
    clearAnalyses,
  }
})
