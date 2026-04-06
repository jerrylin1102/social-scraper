<template>
  <div>
    <!-- Empty -->
    <div v-if="!posts.length" class="card p-10 text-center text-slate-400 text-sm">
      {{ search ? '找不到符合的貼文' : '尚無貼文資料' }}
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <PostCard v-for="post in visible" :key="post.id" :post="post" :platform="platform" />

      <!-- Load more -->
      <button v-if="visible.length < posts.length"
              class="w-full py-3 text-sm text-slate-500 hover:text-slate-800 border border-slate-200 rounded-xl bg-white hover:bg-slate-50 transition-colors"
              @click="page++">
        載入更多（已顯示 {{ visible.length }} / {{ posts.length }}）
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PostCard from './PostCard.vue'

const props = defineProps({ posts: Array, platform: String, search: String })
const page  = ref(1)
const PER   = 20

const visible = computed(() => props.posts.slice(0, page.value * PER))
</script>
