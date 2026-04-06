<template>
  <header class="bg-white border-b border-slate-100 sticky top-0 z-40">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
      <RouterLink to="/" class="flex items-center gap-2 font-bold text-slate-900 text-lg hover:opacity-80 transition-opacity">
        <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><path d="M8.56 2.75c4.37 6.03 6.02 9.42 8.03 17.72m2.54-15.38c-3.72 4.35-8.94 5.66-16.88 5.85m19.5 1.9c-3.5-.93-6.63-.82-8.94 0-2.58.92-5.01 2.86-7.44 6.32"/>
        </svg>
        <span>Social Scraper</span>
      </RouterLink>

      <p class="hidden sm:block text-xs text-slate-400">分析結果只保存在這個瀏覽器</p>
    </div>
  </header>
</template>
