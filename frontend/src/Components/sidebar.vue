<template>
  <aside
    class="relative z-30 flex h-screen shrink-0 overflow-hidden border-r border-slate-800 bg-slate-950 text-slate-100 transition-[width] duration-300"
    :class="expanded ? 'w-[25rem]' : 'w-20'"
  >
    <div class="flex w-20 flex-col items-center justify-between py-4">
      <div class="flex flex-col items-center gap-6">
        <button
          type="button"
          class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 text-slate-100 transition hover:bg-white/15"
          @click="$emit('toggle')"
        >
          <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 7h16M4 12h16M4 17h16" stroke-linecap="round" />
          </svg>
        </button>

        <button type="button" class="text-slate-400 transition hover:text-white" @click="$emit('toggle')">
          <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="7" />
            <circle cx="12" cy="12" r="2" />
          </svg>
        </button>

        <button type="button" class="text-slate-400 transition hover:text-white" @click="$emit('toggle')">
          <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M8 7.5A6.5 6.5 0 0 1 18 13l2 2v2h-3l-1 2h-3" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M9 17H6a2 2 0 0 1-2-2v-1l2-2A6.5 6.5 0 0 1 12 5.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <button type="button" class="text-slate-400 transition hover:text-white" @click="$emit('toggle')">
          <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="10" cy="7" r="3" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M16 4.13a3 3 0 0 1 0 5.75" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <div class="h-px w-10 bg-white/10"></div>

        <button
          type="button"
          class="text-cyan-400 transition hover:text-cyan-300"
          :class="expanded ? 'drop-shadow-[0_0_10px_rgba(34,211,238,0.65)]' : ''"
          @click="$emit('toggle')"
        >
          <svg viewBox="0 0 24 24" class="h-7 w-7" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="8" />
            <path d="M12 4v3M12 17v3M4 12h3M17 12h3" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <div class="flex flex-col items-center gap-5">
        <button type="button" class="text-slate-400 transition hover:text-white" @click="$emit('toggle')">
          <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 16.5V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10.5" stroke-linecap="round" />
            <path d="M8 20h8" stroke-linecap="round" />
            <path d="m8 12 2.5-2.5 2 2 3.5-3.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <button
          type="button"
          class="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/20 text-amber-200 transition hover:bg-amber-500/30"
          @click="$emit('toggle')"
        >
          {{ currentUserInitials }}
        </button>
      </div>
    </div>

    <div
      class="flex min-w-0 flex-1 flex-col overflow-hidden transition-opacity duration-200"
      :class="expanded ? 'opacity-100' : 'pointer-events-none opacity-0'"
    >
      <div class="border-b border-white/10 px-5 py-5">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-500/15 text-lg font-semibold text-emerald-300">
            {{ currentUserInitials }}
          </div>
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-300/80">Call Center</p>
            <p class="truncate text-lg font-semibold text-white">{{ currentUserName }}</p>
          </div>
        </div>

        <div class="mt-5 grid grid-cols-2 gap-3">
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
            <p class="text-[11px] uppercase tracking-[0.24em] text-slate-400">Total Calls</p>
            <p class="mt-2 text-2xl font-semibold text-white">{{ callSummary.call_count || 0 }}</p>
          </div>
          <div class="rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3">
            <p class="text-[11px] uppercase tracking-[0.24em] text-rose-200/80">Missed</p>
            <p class="mt-2 text-2xl font-semibold text-rose-100">{{ callSummary.missed_calls || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto px-4 py-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Call Log</p>
            <p class="mt-1 text-sm text-slate-500">Recent call activity from your workspace</p>
          </div>
          <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
            {{ callLogs.length }}
          </span>
        </div>

        <div v-if="callLogs.length" class="mt-4 space-y-3">
          <button
            v-for="log in callLogs"
            :key="log.call_id"
            type="button"
            class="w-full rounded-2xl border px-3 py-3 text-left transition hover:-translate-y-0.5 hover:border-white/20"
            :class="callCardClass(log)"
            @click="$emit('select-peer', log.peer)"
          >
            <div class="flex items-start gap-3">
              <div class="mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl text-sm font-semibold text-white" :style="{ background: avatarColor(log.peer) }">
                {{ initials(log.peer_name || log.peer) }}
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <p class="truncate text-sm font-semibold text-white">{{ log.peer_name || log.peer }}</p>
                    <p class="mt-1 text-xs text-slate-300/80">
                      {{ log.call_type }} call
                      <span class="mx-1 text-slate-500">•</span>
                      {{ formatTime(log.start_time || log.end_time) || 'Just now' }}
                    </p>
                  </div>

                  <span class="rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em]" :class="statusPillClass(log)">
                    {{ statusLabel(log) }}
                  </span>
                </div>

                <p class="mt-3 text-xs text-slate-300/80">
                  {{ durationLabel(log) }}
                </p>
              </div>
            </div>
          </button>
        </div>

        <div v-else class="mt-4 rounded-3xl border border-dashed border-white/10 bg-white/5 px-4 py-5 text-sm text-slate-400">
          Your recent calls will appear here once you start chatting.
        </div>
      </div>

      <div class="border-t border-white/10 p-4">
        <div class="rounded-3xl border border-white/10 bg-white/5 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Profile</p>

          <div class="mt-4 flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-800 text-sm font-semibold text-white">
              {{ currentUserInitials }}
            </div>
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-white">{{ currentUserName }}</p>
              <p class="truncate text-xs text-slate-400">{{ currentUserEmail }}</p>
            </div>
          </div>

          <button
            type="button"
            class="mt-4 w-full rounded-2xl border border-white/10 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-emerald-400/30 hover:text-white"
            @click="$emit('logout')"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
const props = defineProps({
  callLogs: {
    type: Array,
    default: () => [],
  },
  callSummary: {
    type: Object,
    default: () => ({
      call_count: 0,
      missed_calls: 0,
    }),
  },
  currentUserEmail: {
    type: String,
    default: '',
  },
  currentUserInitials: {
    type: String,
    default: '?',
  },
  currentUserName: {
    type: String,
    default: 'User',
  },
  expanded: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['logout', 'select-peer', 'toggle'])

function initials(name) {
  return (name || '?')
    .trim()
    .split(/\s+/)
    .map(part => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

function avatarColor(name) {
  const palette = ['#16a34a', '#0f766e', '#0284c7', '#7c3aed', '#ea580c']
  let hash = 0
  for (const char of name || '') hash = char.charCodeAt(0) + ((hash << 5) - hash)
  return palette[Math.abs(hash) % palette.length]
}

function isMissedCall(log) {
  return log?.status === 'Missed'
}

function isReceivedCall(log) {
  return log?.direction === 'incoming' && !['Missed', 'Rejected', 'Ringing'].includes(log?.status)
}

function callCardClass(log) {
  if (isMissedCall(log)) {
    return 'border-rose-400/25 bg-rose-500/12'
  }

  if (isReceivedCall(log)) {
    return 'border-emerald-400/25 bg-emerald-500/12'
  }

  return 'border-white/10 bg-white/5'
}

function statusLabel(log) {
  if (isMissedCall(log)) return 'Missed'
  if (isReceivedCall(log)) return 'Received'
  if (log?.direction === 'outgoing' && log?.status === 'Completed') return 'Dialed'
  return log?.status || 'Call'
}

function statusPillClass(log) {
  if (isMissedCall(log)) {
    return 'bg-rose-500/15 text-rose-100'
  }

  if (isReceivedCall(log)) {
    return 'bg-emerald-500/15 text-emerald-100'
  }

  return 'bg-white/10 text-slate-200'
}

function durationLabel(log) {
  if (isMissedCall(log)) return 'Missed call'
  if (isReceivedCall(log)) return `Received • ${log?.duration || '00:00'}`
  if (log?.direction === 'outgoing' && log?.status === 'Completed') {
    return `Outgoing • ${log?.duration || '00:00'}`
  }
  return `${log?.status || 'Call'} • ${log?.duration || '00:00'}`
}

function formatTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
