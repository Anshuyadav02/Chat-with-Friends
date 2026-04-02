<template>
  <div class="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm px-4">
    <div class="w-full max-w-md rounded-3xl bg-white/95 p-8 shadow-2xl">
      <div class="flex flex-col items-center text-center">
        <div class="mb-5 flex h-24 w-24 items-center justify-center rounded-full text-3xl font-semibold text-white" :style="{ background: avatarColor }">
          {{ initials(displayName) }}
        </div>
        <p class="text-2xl font-semibold text-slate-900">{{ displayName }}</p>
        <p class="mt-2 text-sm font-medium text-slate-500">{{ subtitle }}</p>
        <p v-if="durationText && !isRinging" class="mt-1 text-xs uppercase tracking-[0.3em] text-slate-400">
          {{ durationText }}
        </p>
      </div>

      <div v-if="incoming && isRinging" class="mt-8 flex items-center justify-center gap-4">
        <button class="rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30" @click="$emit('accept')">
          Accept
        </button>
        <button class="rounded-full bg-rose-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-rose-500/30" @click="$emit('reject')">
          Reject
        </button>
      </div>

      <div v-else class="mt-8 flex items-center justify-center gap-3">
        <button class="rounded-full border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50" @click="$emit('toggle-mute')">
          {{ mediaState?.muted ? 'Unmute' : 'Mute' }}
        </button>
        <button class="rounded-full border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50" @click="$emit('toggle-speaker')">
          {{ mediaState?.speakerOn ? 'Speaker On' : 'Speaker Off' }}
        </button>
        <button class="rounded-full bg-red-500 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-rose-500/30" @click="$emit('end')">
          End
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  call: {
    type: Object,
    default: () => ({}),
  },
  status: {
    type: String,
    default: 'idle',
  },
  durationText: {
    type: String,
    default: '',
  },
  mediaState: {
    type: Object,
    default: () => ({}),
  },
  incoming: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['accept', 'reject', 'end', 'toggle-mute', 'toggle-speaker'])

const displayName = computed(() => props.call?.remoteName || props.call?.callerName || props.call?.from || 'Unknown caller')
const isRinging = computed(() => ['ringing', 'incoming'].includes(props.status))

const subtitle = computed(() => {
  if (props.status === 'connected') return 'Audio call connected'
  if (props.status === 'connecting') return 'Connecting audio call'
  if (props.status === 'ended') return 'Call ended'
  return props.incoming ? 'Incoming audio call' : 'Ringing audio call'
})

const avatarColor = computed(() => {
  const colors = ['#16a34a', '#0f766e', '#0284c7', '#4f46e5', '#ea580c']
  const seed = displayName.value || ''
  let hash = 0
  for (const char of seed) hash = char.charCodeAt(0) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
})

function initials(name) {
  return (name || '?')
    .trim()
    .split(/\s+/)
    .map(part => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
</script>
