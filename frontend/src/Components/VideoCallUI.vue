<template>
  <div class="fixed inset-0 z-40 bg-slate-950 text-white">
    <video ref="remoteVideoRef" autoplay playsinline class="h-full w-full object-cover" :class="{ 'opacity-30': !hasRemoteVideo }"></video>

    <div class="absolute inset-0 bg-gradient-to-b from-black/70 via-transparent to-black/80"></div>

    <div class="absolute left-5 top-5 max-w-[70%]">
      <p class="text-2xl font-semibold">{{ displayName }}</p>
      <p class="mt-1 text-sm text-white/75">{{ subtitle }}</p>
      <p v-if="durationText && !isRinging" class="mt-1 text-xs uppercase tracking-[0.3em] text-white/55">
        {{ durationText }}
      </p>
    </div>

    <div v-if="!hasRemoteVideo" class="absolute inset-0 flex flex-col items-center justify-center">
      <div class="mb-4 flex h-28 w-28 items-center justify-center rounded-full bg-white/15 text-3xl font-semibold">
        {{ initials(displayName) }}
      </div>
      <p class="text-base text-white/80">Waiting for video feed...</p>
    </div>

    <video ref="localVideoRef" autoplay muted playsinline class="absolute bottom-24 right-5 h-36 w-28 rounded-3xl border border-white/20 bg-black object-cover shadow-2xl md:h-44 md:w-32"></video>

    <div v-if="incoming && isRinging" class="absolute inset-x-0 bottom-8 flex items-center justify-center gap-4 px-4">
      <button class="rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30" @click="$emit('accept')">
        Accept
      </button>
      <button class="rounded-full bg-rose-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-rose-500/30" @click="$emit('reject')">
        Reject
      </button>
    </div>

    <div v-else class="absolute inset-x-0 bottom-8 flex items-center justify-center gap-3 px-4">
      <button class="rounded-full border border-white/20 bg-white/10 px-4 py-3 text-sm font-medium transition hover:bg-white/15" @click="$emit('toggle-mute')">
        {{ mediaState?.muted ? 'Unmute' : 'Mute' }}
      </button>
      <button class="rounded-full border border-white/20 bg-white/10 px-4 py-3 text-sm font-medium transition hover:bg-white/15" @click="$emit('toggle-camera')">
        {{ mediaState?.cameraOn ? 'Camera Off' : 'Camera On' }}
      </button>
      <button class="rounded-full border border-white/20 bg-white/10 px-4 py-3 text-sm font-medium transition hover:bg-white/15" @click="$emit('toggle-screen-share')">
        {{ mediaState?.screenSharing ? 'Stop Share' : 'Share Screen' }}
      </button>
      <button class="rounded-full border border-white/20 bg-white/10 px-4 py-3 text-sm font-medium transition hover:bg-white/15" @click="$emit('toggle-speaker')">
        {{ mediaState?.speakerOn ? 'Speaker On' : 'Speaker Off' }}
      </button>
      <button class="rounded-full bg-red-500 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-rose-500/30" @click="$emit('end')">
        End
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

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
  localStream: {
    type: Object,
    default: null,
  },
  remoteStream: {
    type: Object,
    default: null,
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

defineEmits([
  'accept',
  'reject',
  'end',
  'toggle-mute',
  'toggle-camera',
  'toggle-speaker',
  'toggle-screen-share',
])

const localVideoRef = ref(null)
const remoteVideoRef = ref(null)

const displayName = computed(() => props.call?.remoteName || props.call?.callerName || props.call?.from || 'Unknown caller')
const isRinging = computed(() => ['ringing', 'incoming'].includes(props.status))
const hasRemoteVideo = computed(() => Boolean(props.remoteStream))

const subtitle = computed(() => {
  if (props.status === 'connected') return 'Video call connected'
  if (props.status === 'connecting') return 'Connecting video call'
  if (props.status === 'ended') return 'Call ended'
  return props.incoming ? 'Incoming video call' : 'Ringing video call'
})

function syncLocalVideo(stream) {
  if (localVideoRef.value) {
    localVideoRef.value.srcObject = stream || null
  }
}

function syncRemoteVideo(stream) {
  if (remoteVideoRef.value) {
    remoteVideoRef.value.srcObject = stream || null
    remoteVideoRef.value.muted = !props.mediaState?.speakerOn
  }
}

watch(() => props.localStream, syncLocalVideo, { immediate: true })
watch(() => props.remoteStream, syncRemoteVideo, { immediate: true })

watch(
  () => props.mediaState?.speakerOn,
  speakerOn => {
    if (remoteVideoRef.value) {
      remoteVideoRef.value.muted = !speakerOn
    }
  },
  { immediate: true }
)

onMounted(() => {
  syncLocalVideo(props.localStream)
  syncRemoteVideo(props.remoteStream)
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
