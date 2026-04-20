<template>
  <div class="flex h-dvh flex-col" style="background:#111b21; color:#e9edef;">

    <!-- Header -->
    <div class="flex items-center gap-3 px-4 py-3" style="background:#202c33;">
      <button @click="$router.back()" class="rounded-full p-1 hover:bg-white/10 transition-colors">
        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
      </button>
      <span class="flex-1 text-lg font-semibold tracking-wide">Status</span>
      <button @click="fileInput?.click()" class="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium" style="background:#00a884; color:#fff;">
        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        Add
      </button>
    </div>

    <input ref="fileInput" type="file" accept="image/*,video/*" class="hidden" @change="onFileSelected" />

    <!-- Scrollable list -->
    <div class="flex-1 overflow-y-auto">

      <!-- My Status -->
      <div class="px-4 py-3">
        <div class="flex cursor-pointer items-center gap-3 rounded-xl p-2 hover:bg-white/5 transition-colors" @click="openMyStatus">
          <!-- avatar with ring -->
          <div class="relative h-12 w-12 flex-shrink-0">
            <div class="h-12 w-12 rounded-full flex items-center justify-center text-sm font-bold overflow-hidden"
              :style="{ background: myColor, border: myStatuses.length ? '2.5px solid #00a884' : '2.5px solid #8696a0' }">
              <img v-if="myImage" :src="myImage" class="h-full w-full object-cover" />
              <span v-else style="color:#fff;">{{ myInitials }}</span>
            </div>
            <div class="absolute -bottom-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full" style="background:#00a884;">
              <svg viewBox="0 0 24 24" class="h-3 w-3" fill="white"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium">My Status</p>
            <p class="text-sm" style="color:#8696a0;">
              {{ myStatuses.length ? timeAgo(myStatuses[0].creation) + ' · tap to view' : 'Tap to add a status update' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Recent Updates -->
      <template v-if="unseenGroups.length">
        <p class="px-6 pb-1 pt-2 text-xs font-semibold uppercase tracking-wider" style="color:#8696a0;">Recent updates</p>
        <div v-for="group in unseenGroups" :key="group.owner"
          class="flex cursor-pointer items-center gap-3 px-4 py-2.5 hover:bg-white/5 transition-colors"
          @click="openViewer(group)">
          <div class="h-12 w-12 flex-shrink-0 rounded-full flex items-center justify-center text-sm font-bold overflow-hidden"
            :style="{ background: avatarColor(group.owner), border: '2.5px solid #00a884' }">
            <img v-if="group.owner_image" :src="group.owner_image" class="h-full w-full object-cover" />
            <span v-else style="color:#fff;">{{ initials(group.owner_name) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium truncate">{{ group.owner_name }}</p>
            <p class="text-sm truncate" style="color:#8696a0;">{{ timeAgo(group.statuses[0]?.creation) }}</p>
          </div>
        </div>
      </template>

      <!-- Viewed -->
      <template v-if="seenGroups.length">
        <p class="px-6 pb-1 pt-4 text-xs font-semibold uppercase tracking-wider" style="color:#8696a0;">Viewed</p>
        <div v-for="group in seenGroups" :key="group.owner"
          class="flex cursor-pointer items-center gap-3 px-4 py-2.5 hover:bg-white/5 transition-colors"
          @click="openViewer(group)">
          <div class="h-12 w-12 flex-shrink-0 rounded-full flex items-center justify-center text-sm font-bold overflow-hidden"
            :style="{ background: avatarColor(group.owner), border: '2.5px solid #8696a0' }">
            <img v-if="group.owner_image" :src="group.owner_image" class="h-full w-full object-cover" />
            <span v-else style="color:#fff;">{{ initials(group.owner_name) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium truncate">{{ group.owner_name }}</p>
            <p class="text-sm truncate" style="color:#8696a0;">{{ timeAgo(group.statuses[0]?.creation) }}</p>
          </div>
        </div>
      </template>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="h-6 w-6 animate-spin rounded-full border-2 border-transparent" style="border-top-color:#00a884;"></div>
      </div>
    </div>

    <!-- Upload Preview Modal -->
    <Teleport to="body">
      <div v-if="showUploadModal" class="fixed inset-0 z-50 flex flex-col items-center justify-center" style="background:rgba(0,0,0,0.92);">
        <div class="relative w-full max-w-md rounded-2xl overflow-hidden mx-4" style="background:#202c33;">
          <button @click="cancelUpload" class="absolute right-3 top-3 z-10 rounded-full p-1.5 hover:bg-white/20" style="color:#e9edef;">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
          <div class="flex items-center justify-center" style="min-height:300px; background:#111b21;">
            <video v-if="previewKind === 'video'" :src="previewUrl" controls class="max-h-72 max-w-full object-contain" />
            <img v-else :src="previewUrl" class="max-h-72 max-w-full object-contain" />
          </div>
          <div class="p-4 flex flex-col gap-3">
            <!-- Caption text -->
            <input v-model="caption" type="text" placeholder="Add a caption…"
              class="w-full rounded-xl px-4 py-2.5 text-sm outline-none"
              style="background:#2a3942; color:#e9edef; border:none;" />

            <!-- Text style row -->
            <div class="flex items-center gap-3">
              <!-- Color swatches -->
              <div class="flex gap-1.5 flex-wrap">
                <button v-for="c in textColors" :key="c" @click="captionColor = c"
                  class="h-6 w-6 rounded-full border-2 transition"
                  :style="{ background: c, borderColor: captionColor === c ? '#fff' : 'transparent' }">
                </button>
              </div>
              <!-- Size toggle -->
              <div class="flex gap-1 ml-auto">
                <button v-for="s in ['small','medium','large']" :key="s" @click="captionSize = s"
                  class="rounded-lg px-2 py-1 text-xs font-medium transition"
                  :style="captionSize === s ? 'background:#00a884; color:#fff;' : 'background:#2a3942; color:#8696a0;'">
                  {{ s[0].toUpperCase() }}
                </button>
              </div>
            </div>

            <!-- Background music -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <p class="text-xs font-medium" style="color:#8696a0;">🎵 Background Music</p>
                <button v-if="bgMusicUrl" @click="selectSong(null)" class="text-xs" style="color:#ff5252;">Remove</button>
              </div>

              <!-- Selected song banner -->
              <div v-if="selectedSong" class="flex items-center gap-2 rounded-xl px-3 py-2 mb-2" style="background:#00a884;">
                <img :src="selectedSong.artwork" class="h-8 w-8 rounded-lg object-cover flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold truncate" style="color:#fff;">{{ selectedSong.name }}</p>
                  <p class="text-xs truncate" style="color:rgba(255,255,255,0.7);">{{ selectedSong.artist }}</p>
                </div>
                <svg viewBox="0 0 24 24" class="h-4 w-4 flex-shrink-0" fill="white"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>
              </div>

              <!-- Search bar -->
              <div class="flex items-center gap-2 rounded-xl px-3 py-2 mb-2" style="background:#2a3942;">
                <svg viewBox="0 0 24 24" class="h-4 w-4 flex-shrink-0" fill="currentColor" style="color:#8696a0;"><path d="M15.5 14h-.79l-.28-.27A6.5 6.5 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input v-model="musicQuery" @input="onMusicSearch" type="text" placeholder="Search songs, artists…"
                  class="flex-1 text-xs outline-none bg-transparent" style="color:#e9edef;" />
                <div v-if="musicLoading" class="h-3 w-3 animate-spin rounded-full border border-transparent" style="border-top-color:#8696a0;"></div>
              </div>

              <!-- Song list -->
              <div class="overflow-y-auto rounded-xl" style="max-height:160px; background:#1a2631;">
                <div v-if="!musicResults.length && !musicLoading" class="py-4 text-center text-xs" style="color:#8696a0;">
                  {{ musicQuery ? 'No results' : 'Search for a song above' }}
                </div>
                <div v-for="song in musicResults" :key="song.id"
                  class="flex items-center gap-2.5 px-3 py-2 cursor-pointer hover:bg-white/5 transition-colors"
                  :style="bgMusicUrl === song.previewUrl ? 'background:rgba(0,168,132,0.15);' : ''"
                  @click="selectSong(song)">
                  <img :src="song.artwork" class="h-9 w-9 rounded-lg object-cover flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-medium truncate" style="color:#e9edef;">{{ song.name }}</p>
                    <p class="text-xs truncate" style="color:#8696a0;">{{ song.artist }}</p>
                  </div>
                  <!-- preview play button -->
                  <button @click.stop="togglePreview(song)" class="flex-shrink-0 rounded-full p-1.5 hover:bg-white/10"
                    :style="previewingId === song.id ? 'color:#00a884' : 'color:#8696a0'">
                    <svg v-if="previewingId === song.id" viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                    <svg v-else viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                  </button>
                  <div v-if="bgMusicUrl === song.previewUrl" class="flex-shrink-0">
                    <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor" style="color:#00a884;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </div>
                </div>
              </div>

              <!-- hidden preview audio -->
              <audio ref="previewAudio" @ended="previewingId = ''" style="display:none;" />
            </div>

            <button @click="submitStatus" :disabled="uploading"
              class="rounded-xl py-2.5 font-semibold text-sm"
              :class="uploading ? 'opacity-50' : ''"
              style="background:#00a884; color:#fff;">
              {{ uploading ? 'Posting…' : 'Post Status' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Full-screen Viewer -->
    <Teleport to="body">
      <div v-if="viewerOpen && viewerGroup" class="fixed inset-0 z-50 flex flex-col" style="background:#000;">

        <!-- Progress bars -->
        <div class="flex gap-1 px-3 pt-safe pt-3 pb-1">
          <div v-for="(s, i) in viewerGroup.statuses" :key="s.name"
            class="h-0.5 flex-1 rounded-full overflow-hidden" style="background:rgba(255,255,255,0.3);">
            <div class="h-full rounded-full"
              :style="{ width: i < viewerIndex ? '100%' : i === viewerIndex ? progressPct + '%' : '0%', background:'#fff', transition: i === viewerIndex ? 'none' : undefined }">
            </div>
          </div>
        </div>

        <!-- Header -->
        <div class="flex items-center gap-3 px-3 py-2">
          <div class="h-9 w-9 flex-shrink-0 rounded-full flex items-center justify-center text-xs font-bold overflow-hidden"
            :style="{ background: avatarColor(viewerGroup.owner), border: '2px solid rgba(255,255,255,0.5)' }">
            <img v-if="viewerGroup.owner_image" :src="viewerGroup.owner_image" class="h-full w-full object-cover" />
            <span v-else style="color:#fff;">{{ initials(viewerGroup.owner_name) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold" style="color:#fff;">{{ viewerGroup.is_mine ? 'My Status' : viewerGroup.owner_name }}</p>
            <p class="text-xs" style="color:rgba(255,255,255,0.6);">{{ timeAgo(currentStatus?.creation) }}</p>
          </div>
          <button v-if="viewerGroup.is_mine" @click="confirmDelete" class="rounded-full p-1.5 hover:bg-white/20" style="color:#fff;">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
          </button>
          <button @click="closeViewer" class="rounded-full p-1.5 hover:bg-white/20" style="color:#fff;">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
        </div>

        <!-- Media + tap zones -->
        <div class="relative flex-1 overflow-hidden">
          <img v-if="currentStatus?.media_kind === 'image'" :src="currentStatus.file_url" class="h-full w-full object-contain" />
          <video v-else-if="currentStatus?.media_kind === 'video'" ref="viewerVideo"
            :src="currentStatus.file_url" class="h-full w-full object-contain"
            autoplay @ended="nextStatus" @timeupdate="onVideoTimeUpdate" />
          <!-- tap left to go back -->
          <div class="absolute inset-y-0 left-0 w-1/3" @click="prevStatus"></div>
          <!-- tap center to pause/resume -->
          <div class="absolute inset-y-0 left-1/3 w-1/3 flex items-center justify-center" @click="togglePause">
            <transition name="fade-icon">
              <div v-if="isPaused" class="rounded-full p-3" style="background:rgba(0,0,0,0.45);">
                <svg viewBox="0 0 24 24" class="h-8 w-8" fill="white"><path d="M8 5v14l11-7z"/></svg>
              </div>
            </transition>
          </div>
          <!-- tap right to advance -->
          <div class="absolute inset-y-0 right-0 w-1/3" @click="nextStatus"></div>

          <!-- emoji burst particles -->
          <div class="absolute inset-0 pointer-events-none overflow-hidden">
            <div v-for="p in emojiParticles" :key="p.id"
              class="absolute text-3xl select-none"
              :style="{ left: p.x + 'px', bottom: p.y + 'px', animation: 'emojiBurst 1.2s ease-out forwards', animationDelay: p.delay + 'ms' }">
              {{ p.emoji }}
            </div>
          </div>

          <!-- styled caption overlay -->
          <div v-if="currentStatus?.caption" class="absolute bottom-4 left-0 right-0 px-6 text-center"
            :style="{
              color: currentStatus.caption_color || '#ffffff',
              fontSize: currentStatus.caption_size === 'large' ? '1.25rem' : currentStatus.caption_size === 'small' ? '0.8rem' : '1rem',
              fontWeight: 600,
              textShadow: '0 1px 6px rgba(0,0,0,0.9)',
            }">
            {{ currentStatus.caption }}
          </div>
        </div>

        <!-- background music (hidden) -->
        <audio v-if="currentStatus?.bg_music_url" ref="bgAudio" :src="currentStatus.bg_music_url" loop autoplay style="display:none;" />

        <!-- Reactions + comment bar -->
        <div class="flex items-center gap-2 px-4 py-3" style="background:rgba(0,0,0,0.55); backdrop-filter:blur(6px);">
          <div class="flex gap-1.5">
            <button v-for="emoji in quickEmojis" :key="emoji" @click="onReactionClick($event, emoji)"
              class="text-xl transition-transform hover:scale-125 active:scale-110 rounded-full w-9 h-9 flex items-center justify-center"
              :style="currentStatus?.reactions?.[currentUser] === emoji ? 'background:rgba(255,255,255,0.2)' : ''">
              {{ emoji }}
            </button>
          </div>
          <div class="flex-1"></div>
          <button @click="showComments = !showComments" class="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm" style="background:rgba(255,255,255,0.15); color:#fff;">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
            {{ currentStatus?.comments?.length || 0 }}
          </button>
        </div>

        <!-- Comments panel -->
        <div v-if="showComments" class="absolute inset-x-0 bottom-0 z-10 flex flex-col rounded-t-2xl" style="background:#202c33; max-height:60dvh;">
          <div class="flex items-center justify-between px-4 py-3" style="border-bottom:1px solid rgba(255,255,255,0.08);">
            <span class="font-semibold" style="color:#e9edef;">Comments</span>
            <button @click="showComments = false" style="color:#8696a0;">
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
          </div>
          <div class="flex-1 overflow-y-auto px-4 py-3 space-y-4">
            <div v-if="!currentStatus?.comments?.length" class="py-6 text-center text-sm" style="color:#8696a0;">No comments yet</div>
            <div v-for="c in currentStatus?.comments" :key="c.name || c.timestamp" class="flex gap-2.5">
              <div class="h-8 w-8 flex-shrink-0 rounded-full flex items-center justify-center text-xs font-bold"
                :style="{ background: avatarColor(c.commenter), color:'#fff' }">
                {{ initials(c.commenter) }}
              </div>
              <div>
                <p class="text-xs font-semibold" style="color:#00a884;">{{ c.commenter }}</p>
                <p class="text-sm mt-0.5" style="color:#e9edef;">{{ c.text }}</p>
                <p class="text-xs mt-0.5" style="color:#8696a0;">{{ timeAgo(c.timestamp) }}</p>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 px-3 py-2" style="border-top:1px solid rgba(255,255,255,0.08);">
            <input v-model="commentText" @keyup.enter="submitComment" type="text" placeholder="Add a comment…"
              class="flex-1 rounded-xl px-4 py-2 text-sm outline-none"
              style="background:#2a3942; color:#e9edef; border:none;" />
            <button @click="submitComment" :disabled="!commentText.trim()"
              class="rounded-full p-2 transition-colors"
              :style="commentText.trim() ? 'background:#00a884; color:#fff;' : 'background:#2a3942; color:#8696a0;'">
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
          </div>
        </div>

      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { frappeRequest } from 'frappe-ui'
import { useSocket } from '../socket'
import { session } from '@/data/session'

const router = useRouter()
const currentUser = computed(() => session.user || '')

// ── State ─────────────────────────────────────────────────────────────────────
const loading = ref(false)
const statusGroups = ref([])

const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const previewKind = ref('image')
const caption = ref('')
const captionColor = ref('#ffffff')
const captionSize = ref('medium')
const bgMusicUrl = ref('')
const bgMusicFile = ref(null)
const showUploadModal = ref(false)
const uploading = ref(false)
const bgAudio = ref(null)

const textColors = ['#ffffff','#ffeb3b','#ff5252','#69f0ae','#40c4ff','#ce93d8','#ff6d00']

// Music search (iTunes API)
const musicQuery = ref('')
const musicResults = ref([])
const musicLoading = ref(false)
const selectedSong = ref(null)
const previewAudio = ref(null)
const previewingId = ref('')
let musicDebounce = null

const viewerOpen = ref(false)
const viewerGroup = ref(null)
const viewerIndex = ref(0)
const progressPct = ref(0)
const progressTimer = ref(null)
const viewerVideo = ref(null)
const isPaused = ref(false)
const emojiParticles = ref([])
let particleId = 0

const showComments = ref(false)
const commentText = ref('')

const quickEmojis = ['❤️', '😂', '😮', '👏', '🔥']

// ── Computed ──────────────────────────────────────────────────────────────────
const myGroup = computed(() => statusGroups.value.find(g => g.is_mine) || null)
const myStatuses = computed(() => myGroup.value?.statuses || [])
const myInitials = computed(() => initials(currentUser.value || ''))
const myColor = computed(() => avatarColor(currentUser.value || ''))
const myImage = computed(() => myGroup.value?.owner_image || '')
const unseenGroups = computed(() => statusGroups.value.filter(g => !g.is_mine && !g.all_seen))
const seenGroups = computed(() => statusGroups.value.filter(g => !g.is_mine && g.all_seen))
const currentStatus = computed(() => viewerGroup.value?.statuses?.[viewerIndex.value] || null)

// ── Helpers ───────────────────────────────────────────────────────────────────
function initials(name) {
  if (!name) return '?'
  return name.split(/[\s@.]+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('')
}
function avatarColor(user) {
  const colors = ['#2c6fad','#1e7e62','#7c3aed','#b45309','#be185d','#0369a1','#4d7c0f']
  let h = 0
  for (let i = 0; i < (user || '').length; i++) h = (h * 31 + user.charCodeAt(i)) >>> 0
  return colors[h % colors.length]
}
function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt).getTime()) / 1000
  if (diff < 60) return 'just now'
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago'
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago'
  return Math.floor(diff / 86400) + 'd ago'
}

// ── Load ──────────────────────────────────────────────────────────────────────
async function loadStatuses() {
  loading.value = true
  try {
    const data = await frappeRequest({ url: 'fun.api.get_statuses' })
    statusGroups.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('Failed to load statuses', e)
  } finally {
    loading.value = false
  }
}

// ── Upload ────────────────────────────────────────────────────────────────────
function onFileSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  previewKind.value = file.type.startsWith('video') ? 'video' : 'image'
  caption.value = ''
  showUploadModal.value = true
  e.target.value = ''
  // pre-load trending songs
  fetchSongs('top hits 2024')
}

function cancelUpload() {
  stopPreview()
  showUploadModal.value = false
  selectedFile.value = null
  previewUrl.value = ''
  bgMusicFile.value = null
  bgMusicUrl.value = ''
  selectedSong.value = null
  musicQuery.value = ''
  musicResults.value = []
  captionColor.value = '#ffffff'
  captionSize.value = 'medium'
}

// ── iTunes music search ────────────────────────────────────────────────────────
function normalizeSong(item) {
  return {
    id: item.trackId,
    name: item.trackName,
    artist: item.artistName,
    album: item.collectionName || '',
    artwork: (item.artworkUrl100 || '').replace('100x100', '300x300'),
    previewUrl: item.previewUrl || '',
  }
}

async function fetchSongs(query) {
  musicLoading.value = true
  try {
    // Use iTunes Search API — free, no key required
    const term = encodeURIComponent(query || 'new releases 2024')
    const url = `https://itunes.apple.com/search?term=${term}&entity=song&media=music&limit=30&country=us`
    const resp = await fetch(url)
    const json = await resp.json()
    musicResults.value = (json.results || [])
      .filter(r => r.previewUrl)
      .map(normalizeSong)
  } catch (e) {
    console.error('Music fetch failed', e)
  } finally {
    musicLoading.value = false
  }
}

function onMusicSearch() {
  clearTimeout(musicDebounce)
  musicDebounce = setTimeout(() => {
    fetchSongs(musicQuery.value || 'top hits')
  }, 400)
}

function selectSong(song) {
  stopPreview()
  selectedSong.value = song
  bgMusicUrl.value = song ? song.previewUrl : ''
  // auto-play so user hears it immediately
  if (song?.previewUrl && previewAudio.value) {
    previewAudio.value.src = song.previewUrl
    previewAudio.value.play().catch(() => {})
    previewingId.value = song.id
  }
}

function stopPreview() {
  if (previewAudio.value) {
    previewAudio.value.pause()
    previewAudio.value.currentTime = 0
  }
  previewingId.value = ''
}

function togglePreview(song) {
  if (previewingId.value === song.id) {
    stopPreview()
    return
  }
  stopPreview()
  if (!song.previewUrl) return
  previewAudio.value.src = song.previewUrl
  previewAudio.value.play().catch(() => {})
  previewingId.value = song.id
}

async function uploadFile(file) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('is_private', '0')
  const resp = await fetch('/api/method/fun.api.upload_chat_file', {
    method: 'POST',
    headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
    body: fd,
  })
  const json = await resp.json()
  return json.message || json
}

async function submitStatus() {
  if (!selectedFile.value || uploading.value) return
  uploading.value = true
  try {
    const mediaMsg = await uploadFile(selectedFile.value)

    // Upload music file if user picked a local file
    let finalMusicUrl = bgMusicUrl.value
    if (bgMusicFile.value && bgMusicUrl.value.startsWith('blob:')) {
      const musicMsg = await uploadFile(bgMusicFile.value)
      finalMusicUrl = musicMsg.file_url
    }

    await frappeRequest({
      url: 'fun.api.post_status',
      params: {
        file_url: mediaMsg.file_url,
        media_kind: mediaMsg.media_kind,
        mime_type: mediaMsg.mime_type || '',
        caption: caption.value,
        caption_color: captionColor.value,
        caption_size: captionSize.value,
        bg_music_url: finalMusicUrl,
      },
    })
    showUploadModal.value = false
    selectedFile.value = null
    previewUrl.value = ''
    bgMusicFile.value = null
    bgMusicUrl.value = ''
    captionColor.value = '#ffffff'
    captionSize.value = 'medium'
    await loadStatuses()
  } catch (e) {
    console.error('Upload failed', e)
  } finally {
    uploading.value = false
  }
}

// ── Viewer ────────────────────────────────────────────────────────────────────
function openMyStatus() {
  if (!myStatuses.value.length) { fileInput.value?.click(); return }
  openViewer(myGroup.value)
}

function openViewer(group) {
  viewerGroup.value = group
  viewerIndex.value = 0
  progressPct.value = 0
  showComments.value = false
  commentText.value = ''
  viewerOpen.value = true
  nextTick(() => startProgress())
}

function closeViewer() {
  stopProgress()
  isPaused.value = false
  emojiParticles.value = []
  if (bgAudio.value) { bgAudio.value.pause(); bgAudio.value.src = '' }
  viewerOpen.value = false
  viewerGroup.value = null
  viewerIndex.value = 0
  progressPct.value = 0
  showComments.value = false
}

function prevStatus() {
  if (viewerIndex.value > 0) {
    stopProgress()
    isPaused.value = false
    viewerIndex.value--
    progressPct.value = 0
    showComments.value = false
    nextTick(() => startProgress())
  }
}

function nextStatus() {
  stopProgress()
  isPaused.value = false
  const len = viewerGroup.value?.statuses?.length || 0
  if (viewerIndex.value < len - 1) {
    viewerIndex.value++
    progressPct.value = 0
    showComments.value = false
    nextTick(() => startProgress())
  } else {
    closeViewer()
  }
}

function togglePause() {
  if (!viewerOpen.value) return
  isPaused.value = !isPaused.value
  if (isPaused.value) {
    stopProgress()
    if (viewerVideo.value) viewerVideo.value.pause()
    if (bgAudio.value) bgAudio.value.pause()
  } else {
    if (viewerVideo.value) viewerVideo.value.play().catch(() => {})
    if (bgAudio.value) bgAudio.value.play().catch(() => {})
    startProgress()
  }
}

function startProgress() {
  const s = currentStatus.value
  if (!s) return
  markSeen(s.name)
  if (s.media_kind === 'video') return
  const duration = 15000
  const interval = 80
  let elapsed = (progressPct.value / 100) * duration  // resume from where we paused
  stopProgress()
  progressTimer.value = setInterval(() => {
    if (isPaused.value) return
    elapsed += interval
    progressPct.value = Math.min((elapsed / duration) * 100, 100)
    if (elapsed >= duration) nextStatus()
  }, interval)
}

function stopProgress() {
  if (progressTimer.value) { clearInterval(progressTimer.value); progressTimer.value = null }
}

// ── Emoji burst ────────────────────────────────────────────────────────────────
function spawnEmojiParticles(emoji, anchorEl) {
  const count = 10
  const rect = anchorEl?.getBoundingClientRect?.() || { left: window.innerWidth / 2, bottom: 80, width: 36 }
  const centerX = rect.left + rect.width / 2

  for (let i = 0; i < count; i++) {
    const id = ++particleId
    const spread = (Math.random() - 0.5) * 200
    const delay = Math.random() * 300
    emojiParticles.value.push({ id, emoji, x: centerX + spread - 16, y: 60, delay })
    setTimeout(() => {
      emojiParticles.value = emojiParticles.value.filter(p => p.id !== id)
    }, 1400 + delay)
  }
}

function onVideoTimeUpdate(e) {
  const v = e.target
  if (v.duration) progressPct.value = (v.currentTime / v.duration) * 100
}

async function markSeen(name) {
  try { await frappeRequest({ url: 'fun.api.mark_status_seen', params: { status_name: name } }) } catch {}
}

// ── Reactions ─────────────────────────────────────────────────────────────────
function onReactionClick(event, emoji) {
  const btn = event?.currentTarget
  spawnEmojiParticles(emoji, btn)
  sendReaction(emoji)
}

async function sendReaction(emoji) {
  if (!currentStatus.value) return
  const current = currentStatus.value.reactions?.[currentUser.value]
  const send = current === emoji ? '' : emoji
  try {
    const res = await frappeRequest({ url: 'fun.api.react_to_status', params: { status_name: currentStatus.value.name, emoji: send } })
    if (res?.reactions !== undefined) currentStatus.value.reactions = res.reactions
  } catch (e) { console.error(e) }
}

// ── Comments ──────────────────────────────────────────────────────────────────
async function submitComment() {
  const text = commentText.value.trim()
  if (!text || !currentStatus.value) return
  try {
    const comment = await frappeRequest({ url: 'fun.api.comment_on_status', params: { status_name: currentStatus.value.name, text } })
    if (!currentStatus.value.comments) currentStatus.value.comments = []
    currentStatus.value.comments.push(comment)
    commentText.value = ''
  } catch (e) { console.error(e) }
}

// ── Delete ────────────────────────────────────────────────────────────────────
async function confirmDelete() {
  if (!currentStatus.value) return
  if (!confirm('Delete this status?')) return
  try {
    await frappeRequest({ url: 'fun.api.delete_status', params: { status_name: currentStatus.value.name } })
    const idx = viewerGroup.value.statuses.findIndex(s => s.name === currentStatus.value.name)
    if (idx !== -1) viewerGroup.value.statuses.splice(idx, 1)
    if (!viewerGroup.value.statuses.length) {
      closeViewer()
      await loadStatuses()
    } else {
      viewerIndex.value = Math.min(viewerIndex.value, viewerGroup.value.statuses.length - 1)
      progressPct.value = 0
      nextTick(() => startProgress())
    }
  } catch (e) { console.error(e) }
}

// ── Socket ────────────────────────────────────────────────────────────────────
let socket = null
function setupSocket() {
  try {
    socket = useSocket()
    if (!socket) return
    socket.on('new_status', () => loadStatuses())
    socket.on('status_deleted', ({ status_name }) => {
      statusGroups.value.forEach(g => {
        const i = g.statuses.findIndex(s => s.name === status_name)
        if (i !== -1) g.statuses.splice(i, 1)
      })
      statusGroups.value = statusGroups.value.filter(g => g.statuses.length > 0)
      if (viewerOpen.value && currentStatus.value?.name === status_name) nextStatus()
    })
    socket.on('status_reacted', ({ status_name, reactions }) => {
      statusGroups.value.forEach(g => {
        const s = g.statuses.find(x => x.name === status_name)
        if (s) s.reactions = reactions
      })
    })
    socket.on('status_commented', ({ status_name, comment }) => {
      statusGroups.value.forEach(g => {
        const s = g.statuses.find(x => x.name === status_name)
        if (s) { if (!s.comments) s.comments = []; s.comments.push(comment) }
      })
    })
  } catch (e) { console.warn('Socket unavailable', e) }
}

onMounted(() => { loadStatuses(); setupSocket() })
onUnmounted(() => {
  stopProgress()
  stopPreview()
  clearTimeout(musicDebounce)
  if (socket) {
    socket.off('new_status')
    socket.off('status_deleted')
    socket.off('status_reacted')
    socket.off('status_commented')
  }
})

watch(showComments, open => {
  if (open) stopProgress()
  else if (viewerOpen.value && !isPaused.value) startProgress()
})
</script>

<style scoped>
@keyframes emojiBurst {
  0%   { transform: translateY(0) scale(1);    opacity: 1; }
  60%  { transform: translateY(-90px) scale(1.4); opacity: 1; }
  100% { transform: translateY(-150px) scale(0.6); opacity: 0; }
}

.fade-icon-enter-active, .fade-icon-leave-active { transition: opacity 0.2s; }
.fade-icon-enter-from, .fade-icon-leave-to       { opacity: 0; }
</style>
