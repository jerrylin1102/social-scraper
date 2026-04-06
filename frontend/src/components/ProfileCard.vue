<template>
  <div
    class="card p-5 cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 animate-slide-up group"
    @click="$emit('click')"
  >
    <div class="flex items-start gap-3">
      <!-- Avatar -->
      <div class="relative shrink-0">
        <img v-if="profile.profile_pic_local" :src="profile.profile_pic_local" :alt="profile.username"
             class="w-14 h-14 rounded-full object-cover ring-2 ring-slate-100" />
        <div v-else
             class="w-14 h-14 rounded-full flex items-center justify-center text-xl font-bold text-white"
             :class="profile.platform === 'threads' ? 'bg-black' : 'bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400'">
          {{ (profile.username[0] || '?').toUpperCase() }}
        </div>

        <!-- Platform dot -->
        <span class="absolute -bottom-0.5 -right-0.5 w-5 h-5 rounded-full border-2 border-white flex items-center justify-center text-white text-[8px] font-bold"
              :class="profile.platform === 'threads' ? 'bg-black' : 'bg-gradient-to-br from-purple-500 to-orange-400'">
          {{ profile.platform === 'threads' ? 'T' : 'IG' }}
        </span>
      </div>

      <!-- Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-1.5">
          <p class="font-semibold text-slate-900 truncate">{{ profile.full_name || profile.username }}</p>
          <svg v-if="profile.is_verified" class="w-4 h-4 text-blue-500 shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <p class="text-xs text-slate-400 mb-2">@{{ profile.username }}</p>
        <p v-if="profile.bio" class="text-xs text-slate-600 line-clamp-2">{{ profile.bio }}</p>
      </div>

      <!-- Delete btn -->
      <button class="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-lg hover:bg-red-50 text-red-400"
              @click.stop="$emit('delete')" title="刪除">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      </button>
    </div>

    <!-- Stats -->
    <div class="flex gap-4 mt-4 pt-4 border-t border-slate-50">
      <div>
        <p class="text-xs text-slate-400">追蹤者</p>
        <p class="text-sm font-semibold text-slate-800">{{ fmt(profile.followers_count) }}</p>
      </div>
      <div>
        <p class="text-xs text-slate-400">貼文數</p>
        <p class="text-sm font-semibold text-slate-800">{{ fmt(profile.posts_count) }}</p>
      </div>
      <div class="ml-auto text-right">
        <p class="text-xs text-slate-400">爬取時間</p>
        <p class="text-xs text-slate-500">{{ fmtDate(profile.scraped_at) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ profile: Object })
defineEmits(['click', 'delete'])

const fmt = n => n >= 1_000_000 ? (n/1_000_000).toFixed(1)+'M'
               : n >= 1_000     ? (n/1_000).toFixed(1)+'K' : (n??0).toString()
const fmtDate = d => d ? new Date(d).toLocaleDateString('zh-TW') : ''
</script>
