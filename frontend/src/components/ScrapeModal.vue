<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in"
         @click.self="$emit('close')">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md animate-slide-up">

        <!-- Header -->
        <div class="flex items-center justify-between px-6 pt-6 pb-4 border-b border-slate-100">
          <h3 class="font-bold text-slate-900 text-lg">新增爬取</h3>
          <button class="text-slate-400 hover:text-slate-600 transition-colors p-1" @click="$emit('close')">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="px-6 py-5 space-y-4">
          <!-- Platform -->
          <div>
            <label class="text-sm font-medium text-slate-700 mb-2 block">平台</label>
            <div class="grid grid-cols-2 gap-2">
              <button v-for="p in platforms" :key="p.value"
                      @click="platform = p.value"
                      :class="['flex items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all text-sm font-medium',
                               platform === p.value
                                 ? p.activeClass
                                 : 'border-slate-200 text-slate-600 hover:border-slate-300']">
                <span v-html="p.icon" class="w-5 h-5 flex-shrink-0"/>
                {{ p.label }}
              </button>
            </div>
          </div>

          <!-- Username -->
          <div>
            <label class="text-sm font-medium text-slate-700 mb-2 block">帳號名稱</label>
            <div class="flex items-center border-2 rounded-xl transition-colors"
                 :class="focused ? 'border-slate-400' : 'border-slate-200'">
              <span class="pl-3 text-slate-400 text-sm">@</span>
              <input v-model="username" ref="inputRef" type="text" placeholder="輸入帳號…"
                     class="flex-1 px-2 py-3 text-sm bg-transparent outline-none text-slate-900 placeholder-slate-400"
                     @focus="focused=true" @blur="focused=false"
                     @keyup.enter="submit" />
            </div>
          </div>

          <!-- Error -->
          <p v-if="errorMsg" class="text-red-500 text-sm bg-red-50 rounded-lg px-3 py-2">{{ errorMsg }}</p>

          <!-- Info -->
          <p class="text-xs text-slate-400">只支援公開帳號，爬取可能需要 15–60 秒。</p>
        </div>

        <!-- Footer -->
        <div class="px-6 pb-6 flex gap-3">
          <button class="btn-ghost flex-1" @click="$emit('close')" :disabled="loading">取消</button>
          <button class="btn-primary flex-1 justify-center" @click="submit" :disabled="loading || !username.trim()">
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            {{ loading ? '爬取中…' : '開始爬取' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useScraperStore } from '@/stores/scraper'

const emit    = defineEmits(['close', 'done'])
const store   = useScraperStore()
const platform = ref('threads')
const username = ref('')
const loading  = ref(false)
const errorMsg = ref('')
const focused  = ref(false)
const inputRef = ref(null)

const platforms = [
  {
    value: 'threads', label: 'Threads',
    activeClass: 'border-black bg-black text-white',
    icon: `<svg viewBox="0 0 192 192" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M141.537 88.988a66.667 66.667 0 0 0-2.518-1.143c-1.482-27.307-16.403-42.94-41.457-43.1h-.34c-14.986 0-27.449 6.396-35.12 18.036l13.779 9.452c5.73-8.695 14.724-10.548 21.348-10.548h.23c8.249.053 14.474 2.452 18.502 7.13 2.932 3.405 4.893 8.111 5.864 14.05-7.314-1.243-15.224-1.626-23.68-1.14-23.82 1.371-39.134 15.264-38.105 34.568.522 9.792 5.4 18.216 13.735 23.719 7.047 4.652 16.124 6.927 25.557 6.412 12.458-.683 22.231-5.436 29.049-14.127 5.178-6.6 8.453-15.153 9.899-25.93 5.937 3.583 10.337 8.298 12.767 13.966 4.132 9.635 4.373 25.468-8.546 38.376-11.319 11.308-24.925 16.2-45.488 16.351-22.809-.169-40.06-7.484-51.275-21.742C35.236 139.966 29.808 120.682 29.605 96c.203-24.682 5.63-43.966 16.133-57.317C56.954 24.425 74.204 17.11 97.013 16.94c22.975.17 40.526 7.52 52.171 21.847 5.71 7.026 10.015 15.86 12.853 26.162l16.147-4.308c-3.44-12.68-8.853-23.606-16.219-32.668C147.036 9.607 125.202.195 97.07 0h-.1C68.976.195 47.394 9.643 32.81 28.08 19.883 44.485 13.224 67.315 13.001 95.932L13 96l.001.068c.223 28.617 6.882 51.447 19.809 67.852C47.394 182.357 68.976 191.805 96.97 192h.1c24.96-.173 42.554-6.708 57.048-21.189 18.963-18.944 18.392-42.509 12.142-57.01-4.484-10.454-13.033-18.945-24.723-24.813ZM98.44 129.507c-10.44.588-21.286-4.098-21.82-14.135-.397-7.442 5.296-15.746 22.461-16.735 1.966-.113 3.895-.169 5.79-.169 6.235 0 12.068.606 17.371 1.765-1.978 24.702-13.58 28.713-23.802 29.274Z"/></svg>`,
  },
  {
    value: 'instagram', label: 'Instagram',
    activeClass: 'border-pink-500 bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 text-white',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`,
  },
]

onMounted(() => nextTick(() => inputRef.value?.focus()))

async function submit() {
  if (!username.value.trim() || loading.value) return
  errorMsg.value = ''
  loading.value  = true
  try {
    const res = await store.scrape(platform.value, username.value.trim())
    emit('done', res)
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
