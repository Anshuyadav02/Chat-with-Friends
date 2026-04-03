<template>
  <div class="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm px-4">
    <div class="w-full max-w-sm rounded-3xl overflow-hidden shadow-2xl" style="background:#1c2b36">

      <!-- Avatar + name -->
      <div class="flex flex-col items-center px-8 pt-10 pb-6 text-center">
        <div
          class="mb-4 flex h-24 w-24 items-center justify-center rounded-full text-3xl font-semibold text-white shadow-lg"
          :style="{ background: avatarColor }"
        >
          {{ initials(displayName) }}
        </div>
        <p class="text-xl font-semibold text-white">{{ displayName }}</p>
        <p class="mt-1 text-sm font-medium" style="color:#8696a0">{{ subtitle }}</p>
        <p v-if="durationText && !isRinging" class="mt-1 text-xs uppercase tracking-[0.3em]" style="color:#00a884">
          {{ durationText }}
        </p>
      </div>

      <!-- Incoming ringing -->
      <div v-if="incoming && isRinging" class="flex items-center justify-center gap-6 px-8 pb-10">
        <div class="flex flex-col items-center gap-2">
          <button
            class="flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition active:scale-95"
            style="background:#f15c6d"
            @click="$emit('reject')"
          >
            <!-- end call icon -->
            <svg viewBox="0 0 24 24" class="h-6 w-6 text-white" fill="currentColor">
              <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08A.99.99 0 0 1 0 12.37c0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.66c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28a11.27 11.27 0 0 0-2.67-1.85.999.999 0 0 1-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
            </svg>
          </button>
          <span class="text-xs" style="color:#8696a0">Decline</span>
        </div>

        <div class="flex flex-col items-center gap-2">
          <button
            class="flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition active:scale-95"
            style="background:#00a884"
            @click="$emit('accept')"
          >
            <!-- phone icon -->
            <svg viewBox="0 0 24 24" class="h-6 w-6 text-white" fill="currentColor">
              <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
            </svg>
          </button>
          <span class="text-xs" style="color:#8696a0">Accept</span>
        </div>
      </div>

      <!-- Active call controls -->
      <div v-else class="px-6 pb-10">
        <!-- Control buttons row -->
        <div class="mb-6 flex items-center justify-center gap-4">

          <!-- Mute -->
          <div class="flex flex-col items-center gap-1.5">
            <button
              class="ctrl-btn flex h-12 w-12 items-center justify-center rounded-full transition active:scale-95"
              :class="mediaState?.muted ? 'ctrl-active' : 'ctrl-idle'"
              @click="$emit('toggle-mute')"
            >
              <svg v-if="mediaState?.muted" viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3 3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
              </svg>
            </button>
            <span class="text-[11px]" style="color:#8696a0">{{ mediaState?.muted ? 'Unmute' : 'Mute' }}</span>
          </div>

          <!-- Speaker -->
          <div class="flex flex-col items-center gap-1.5">
            <button
              class="ctrl-btn flex h-12 w-12 items-center justify-center rounded-full transition active:scale-95"
              :class="mediaState?.speakerOn ? 'ctrl-active' : 'ctrl-idle'"
              @click="$emit('toggle-speaker')"
            >
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
              </svg>
            </button>
            <span class="text-[11px]" style="color:#8696a0">Speaker</span>
          </div>

          <!-- Camera (upgrade to video) -->
          <div class="flex flex-col items-center gap-1.5">
            <button
              class="ctrl-btn flex h-12 w-12 items-center justify-center rounded-full transition active:scale-95"
              :class="mediaState?.cameraOn ? 'ctrl-active' : 'ctrl-idle'"
              @click="$emit('toggle-camera')"
            >
              <svg v-if="mediaState?.cameraOn" viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                <path d="M21 6.5l-4-4-1.45 1.45L17 5.4V7h-2.17l2 2H17v.17l1.83 1.83H19v-3.5l4 4v-4.5zM3.27 2 2 3.27l1.27 1.27C2.56 4.69 2 5.28 2 6v12c0 1.1.9 2 2 2h16c.28 0 .54-.06.79-.15L22.73 22 24 20.73 3.27 2zM4 18V6h.73L18 19.27c-.09.04-.19.07-.3.07-.11 0-.21-.03-.3-.07L4 18z"/>
              </svg>
            </button>
            <span class="text-[11px]" style="color:#8696a0">Camera</span>
          </div>

        </div>

        <!-- End call button -->
        <div class="flex justify-center">
          <div class="flex flex-col items-center gap-1.5">
            <button
              class="flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition active:scale-95"
              style="background:#f15c6d"
              @click="$emit('end')"
            >
              <svg viewBox="0 0 24 24" class="h-6 w-6 text-white" fill="currentColor">
                <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08A.99.99 0 0 1 0 12.37c0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.66c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28a11.27 11.27 0 0 0-2.67-1.85.999.999 0 0 1-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
              </svg>
            </button>
            <span class="text-[11px]" style="color:#8696a0">End call</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  call:        { type: Object, default: () => ({}) },
  status:      { type: String, default: 'idle' },
  durationText:{ type: String, default: '' },
  mediaState:  { type: Object, default: () => ({}) },
  incoming:    { type: Boolean, default: false },
})

defineEmits(['accept', 'reject', 'end', 'toggle-mute', 'toggle-speaker', 'toggle-camera'])

const displayName = computed(() =>
  props.call?.remoteName || props.call?.callerName || props.call?.from || 'Unknown caller'
)
const isRinging = computed(() => ['ringing', 'incoming'].includes(props.status))

const subtitle = computed(() => {
  if (props.status === 'connected')  return 'Voice call connected'
  if (props.status === 'connecting') return 'Connecting…'
  if (props.status === 'ended')      return 'Call ended'
  return props.incoming ? 'Incoming voice call' : 'Calling…'
})

const avatarColor = computed(() => {
  const colors = ['#00a884','#0f766e','#0284c7','#7c3aed','#ea580c']
  const seed = displayName.value || ''
  let hash = 0
  for (const char of seed) hash = char.charCodeAt(0) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
})

function initials(name) {
  return (name || '?').trim().split(/\s+/).map(p => p[0]).slice(0, 2).join('').toUpperCase()
}
</script>

<style scoped>
.ctrl-btn { }
.ctrl-idle  { background: rgba(255,255,255,0.08); color: #e9edef; }
.ctrl-idle:hover { background: rgba(255,255,255,0.14); }
.ctrl-active { background: rgba(0,168,132,0.2); color: #00a884; }
.ctrl-active:hover { background: rgba(0,168,132,0.3); }
</style>
