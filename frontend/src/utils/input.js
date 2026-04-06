function parseUrl(raw) {
  const value = `${raw || ''}`.trim()
  if (!value) return null

  try {
    return new URL(value.startsWith('http') ? value : `https://${value}`)
  } catch {
    return null
  }
}

export function parseSocialInput(raw) {
  const value = `${raw || ''}`.trim()
  if (!value) {
    return { username: '', platform: null, isUrl: false }
  }

  const parsed = parseUrl(value)
  if (!parsed) {
    return {
      username: value.replace(/^@/, '').trim(),
      platform: null,
      isUrl: false,
    }
  }

  const host = parsed.hostname.toLowerCase()
  const parts = parsed.pathname.split('/').filter(Boolean)

  if (host.includes('threads.net')) {
    const first = parts[0] || ''
    return {
      username: first.replace(/^@/, '').trim(),
      platform: 'threads',
      isUrl: true,
    }
  }

  if (host.includes('instagram.com')) {
    const reservedPaths = new Set(['p', 'reel', 'reels', 'stories', 'explore', 'accounts', 'direct'])
    const first = (parts[0] || '').replace(/^@/, '').trim()
    return {
      username: reservedPaths.has(first.toLowerCase()) ? '' : first,
      platform: reservedPaths.has(first.toLowerCase()) ? null : 'instagram',
      isUrl: true,
    }
  }

  return {
    username: value.replace(/^@/, '').trim(),
    platform: null,
    isUrl: false,
  }
}
