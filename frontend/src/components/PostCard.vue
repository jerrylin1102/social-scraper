<template>
  <div class="card px-5 py-4 hover:shadow-sm transition-shadow">
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1 min-w-0">
        <!-- Text -->
        <p v-if="post.text" class="text-sm text-slate-800 whitespace-pre-wrap leading-relaxed">
          {{ expanded ? post.text : truncated }}
        </p>
        <p v-else class="text-sm text-slate-400 italic">（無文字內容）</p>

        <!-- Expand -->
        <button v-if="isLong" @click="expanded = !expanded"
                class="text-xs text-slate-400 hover:text-slate-600 mt-1 transition-colors">
          {{ expanded ? '收起' : '展開全文' }}
        </button>
      </div>

      <!-- Link -->
      <a v-if="post.post_url" :href="post.post_url" target="_blank"
         class="shrink-0 text-slate-300 hover:text-slate-500 transition-colors" title="開啟原始貼文">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
        </svg>
      </a>
    </div>

    <!-- Meta -->
    <div class="flex items-center gap-4 mt-3 text-xs text-slate-400">
      <span>{{ fmtDate(post.created_at) }}</span>
      <span v-if="post.like_count" class="flex items-center gap-1">
        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
        </svg>
        {{ fmt(post.like_count) }}
      </span>
      <span v-if="post.reply_count" class="flex items-center gap-1">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
        {{ fmt(post.reply_count) }}
      </span>
      <span v-if="platform === 'threads' && post.repost_count" class="flex items-center gap-1">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        {{ fmt(post.repost_count) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ post: Object, platform: String })
const expanded = ref(false)

const LIMIT = 200
const isLong = computed(() => (props.post?.text?.length ?? 0) > LIMIT)
const truncated = computed(() =>
  isLong.value ? props.post.text.slice(0, LIMIT) + '…' : props.post?.text
)

const fmt = n => n >= 1_000_000 ? (n/1_000_000).toFixed(1)+'M'
               : n >= 1_000     ? (n/1_000).toFixed(1)+'K' : (n??0).toString()
const fmtDate = d => d ? new Date(d).toLocaleString('zh-TW', { dateStyle:'short', timeStyle:'short' }) : ''
</script>
