<template>
  <header class="bg-white/80 backdrop-blur-md border-b border-slate-100 sticky top-0 z-40 transition-all">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
      <RouterLink to="/" class="flex items-center gap-2 font-bold text-lg hover:opacity-80 transition-opacity group">
        <div class="bg-gradient-to-tr from-indigo-500 to-pink-500 text-white rounded-xl p-1.5 shadow-sm group-hover:scale-105 transition-transform">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"/><path d="M8.56 2.75c4.37 6.03 6.02 9.42 8.03 17.72m2.54-15.38c-3.72 4.35-8.94 5.66-16.88 5.85m19.5 1.9c-3.5-.93-6.63-.82-8.94 0-2.58.92-5.01 2.86-7.44 6.32"/>
          </svg>
        </div>
        <span class="bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600 tracking-tight">Social Scraper</span>
      </RouterLink>

      <div class="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-50 border border-slate-100">
        <svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <p class="text-[11px] font-medium text-slate-500">本機安全儲存</p>
      </div>
    </div>
  </header>
</template>
