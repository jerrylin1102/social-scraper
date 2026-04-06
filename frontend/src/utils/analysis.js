import { withBackendBase } from '@/utils/backend'

export function formatNumber(value) {
  const number = Number(value || 0)
  if (number >= 1_000_000) return `${(number / 1_000_000).toFixed(1)}M`
  if (number >= 1_000) return `${(number / 1_000).toFixed(1)}K`
  return `${number}`
}

export function formatDate(value, options = { dateStyle: 'medium', timeStyle: 'short' }) {
  if (!value) return ''
  return new Date(value).toLocaleString('zh-TW', options)
}

export function platformLabel(platform) {
  return platform === 'threads' ? 'Threads' : 'Instagram'
}

export function platformBadgeClass(platform) {
  return platform === 'threads' ? 'badge-threads' : 'badge-instagram'
}

export function getSuccessfulSources(results = []) {
  return results.filter(item => item.success && item.profile)
}

export function getPrimarySource(results = []) {
  const successful = getSuccessfulSources(results)
  return successful.find(item => item.profile?.profile_pic_local)
    || successful.find(item => item.profile?.profile_pic_url)
    || successful.find(item => item.platform === 'instagram')
    || successful[0]
    || null
}

export function getDisplayName(results = [], fallback = '') {
  const primary = getPrimarySource(results)
  return primary?.profile?.full_name || primary?.profile?.username || fallback
}

export function getAvatar(profile) {
  return withBackendBase(profile?.profile_pic_local || profile?.profile_pic_url || '')
}

export function normalizePlatforms(platforms = []) {
  return [...new Set(platforms.map(platform => `${platform}`.toLowerCase()))]
}
