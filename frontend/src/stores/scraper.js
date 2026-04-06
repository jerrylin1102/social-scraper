import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useScraperStore = defineStore('scraper', () => {
  const profiles  = ref([])
  const loading   = ref(false)
  const error     = ref(null)

  async function fetchProfiles() {
    try {
      const { data } = await axios.get('/api/profiles')
      profiles.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || '讀取失敗'
    }
  }

  async function scrape(platform, username) {
    loading.value = true
    error.value   = null
    try {
      const { data } = await axios.post('/api/scrape', { platform, username }, { timeout: 120_000 })
      // Refresh list
      await fetchProfiles()
      return data
    } catch (e) {
      const msg = e.response?.data?.detail || '爬取失敗，請稍後再試。'
      error.value = msg
      throw new Error(msg)
    } finally {
      loading.value = false
    }
  }

  async function getProfile(platform, username) {
    const { data } = await axios.get(`/api/profiles/${platform}/${username}`)
    return data
  }

  async function deleteProfile(platform, username) {
    await axios.delete(`/api/profiles/${platform}/${username}`)
    profiles.value = profiles.value.filter(
      p => !(p.platform === platform && p.username === username)
    )
  }

  return { profiles, loading, error, fetchProfiles, scrape, getProfile, deleteProfile }
})
