<template>
  <div class="flex h-screen overflow-hidden bg-gray-100">
    <Sidebar
      :call-logs="sidebarCallLogs"
      :call-summary="recentCallSummary"
      :clearing-call-logs="clearingCallLogs"
      :current-user-email="session.user || ''"
      :current-user-initials="currentUserInitials"
      :current-user-name="currentUserName"
      :deleting-call-id="deletingCallId"
      :deleting-selected-call-logs="deletingSelectedCallLogsState"
      :expanded="sidebarExpanded"
      @clear-logs="clearAllCallLogs"
      @delete-log="deleteCallLog"
      @delete-selected="deleteSelectedCallLogs"
      @logout="logout"
      @select-peer="focusPeer"
      @call-peer="({ peer, type }) => { focusPeer(peer); startCall(resolveUser(peer), type).catch(console.error) }"
      @toggle="sidebarExpanded = !sidebarExpanded"
    />

    <div class="flex flex-1 overflow-hidden">
      <div
        class="fixed z-20 flex h-full w-72 transform flex-col border-r border-gray-200 bg-white transition-transform duration-300 sm:w-80 md:relative md:translate-x-0"
        :class="selectedUser ? '-translate-x-full md:translate-x-0' : 'translate-x-0'"
      >
        <div class="flex items-center justify-between bg-green-600 px-4 py-3">
          
          <!-- <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/30 text-sm font-bold text-white">
              {{ currentUserInitials }}
            </div>
            <span class="max-w-[120px] truncate text-sm font-semibold text-white">
              {{ currentUserName }}
            </span> 
          </div> -->
          <span class="max-w-[120px] truncate text-sm font-semibold text-white">
              Chat With Friends
          </span>
        </div>

        <div class="border-b border-gray-100 bg-gray-50 px-3 py-2">
          <input
            v-model="search"
            type="text"
            placeholder="Search"
            class="w-full rounded-full border border-gray-200 bg-white px-4 py-2 text-sm outline-none focus:ring-1 focus:ring-green-400"
          />
        </div>

        <div class="flex-1 overflow-y-auto">
          <div
            v-for="user in filteredUsers"
            :key="user.name"
            class="relative flex cursor-pointer items-center gap-3 border-b px-3 py-3 hover:bg-gray-50 sm:px-4"
            :class="{ 'border-l-4 border-l-green-500 bg-green-50': selectedUser?.name === user.name }"
            @click="selectUser(user)"
          >
            <div class="relative">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white sm:h-11 sm:w-11"
                :style="{ background: avatarColor(user.name) }"
              >
                {{ initials(user.full_name || user.first_name || user.name) }}
              </div>
              <div
                v-if="onlineUsers.includes(user.name)"
                class="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-green-500"
              ></div>
            </div>

            <div class="min-w-0 flex-1">
              <div class="flex justify-between gap-2">
                <span class="truncate text-sm font-medium text-gray-800">
                  {{ user.name === session.user ? 'You' : (user.full_name || user.first_name || user.name) }}
                </span>
                <div class="flex items-center gap-1">
                  <span class="text-xs text-gray-400">
                    {{ formatTime(lastMessageMap[user.name]?.timestamp) }}
                  </span>
                  <span
                    v-if="unreadCount[user.name]"
                    class="min-w-[18px] rounded-full bg-green-500 px-1 text-center text-xs text-white"
                  >
                    {{ unreadCount[user.name] }}
                  </span>
                </div>
              </div>
              <p class="truncate text-xs text-gray-400">
                {{ lastMessageMap[user.name]?.last_message || 'Start chat' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="flex w-full flex-1 flex-col">
        <div v-if="!selectedUser" class="flex flex-1 items-center justify-center text-center">
          <div>
            <div class="mb-3 text-5xl">💬</div>
            <p class="text-gray-500">Select a chat</p>
          </div>
        </div>

        <template v-else>
          <div class="flex items-center gap-3 bg-green-600 px-3 py-3 sm:px-4">
            <button class="text-lg text-white md:hidden" @click="selectedUser = null">←</button>

            <div
              class="flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold text-white"
              :style="{ background: avatarColor(selectedUser.name) }"
            >
              {{ initials(selectedUser.full_name || selectedUser.name) }}
            </div>

            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-white">
                {{ selectedUser.full_name || selectedUser.name }}
              </p>
              <p class="truncate text-xs text-green-200">
                {{ typingUsers[selectedUser.name] ? 'typing...' : (onlineUsers.includes(selectedUser.name) ? 'online' : 'offline') }}
              </p>
            </div>

            <div class="ml-auto flex gap-2">
              <button class="text-lg text-white hover:text-green-200" title="Voice Call" @click="startVoiceCall">📞</button>
              <button class="text-lg text-white hover:text-green-200" title="Video Call" @click="startVideoCall">📹</button>
            </div>
          </div>

          <!-- <div class="border-b bg-white px-4 py-3">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-gray-400">Call History</p>
                <p class="text-sm text-gray-600">
                  {{ callSummary.call_count }} calls, {{ callSummary.missed_calls }} missed
                </p>
              </div>
              <p v-if="isInCall" class="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">
                {{ callStatusLabel }}
              </p>
            </div>

            <div v-if="callLogs.length" class="mt-3 flex gap-2 overflow-x-auto pb-1">
              <div
                v-for="log in callLogs"
                :key="log.call_id"
                class="min-w-[180px] rounded-2xl border border-gray-200 bg-gray-50 px-3 py-2"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="text-sm font-semibold text-gray-700">{{ log.call_type }}</span>
                  <span class="text-[11px] uppercase tracking-[0.2em] text-gray-400">{{ log.direction }}</span>
                </div>
                <p class="mt-1 text-xs text-gray-500">{{ log.status }}</p>
                <p class="mt-1 text-xs text-gray-400">
                  {{ log.duration || '00:00' }} · {{ formatTime(log.start_time || log.end_time) }}
                </p>
              </div>
            </div>
            <p v-else class="mt-3 text-sm text-gray-400">No calls with this user yet.</p>
          </div> -->

          <div ref="messagesContainer" class="flex-1 overflow-y-auto px-2 py-3 sm:px-4" style="background:#e5ddd5">
            <div v-for="group in messageGroups" :key="group.conversation_name">
              <div class="my-3 text-center text-xs text-gray-500">
                {{ formatDateLabel(group.start_date) }}
              </div>

              <div
                v-for="(msg, index) in group.messages"
                :key="`${group.conversation_name}-${index}`"
                class="mb-3 flex flex-col"
                :class="msg.sender === session.user ? 'items-end' : 'items-start'"
              >
                <div
                  class="max-w-[80%] rounded-2xl px-3 py-2 text-sm shadow sm:max-w-md"
                  :class="messageBubbleClass(msg)"
                >
                  <template v-if="msg.attachment">
                    <img
                      v-if="isImageMessage(msg)"
                      :src="msg.attachment.file_url"
                      :alt="msg.attachment.file_name || 'Image attachment'"
                      class="max-h-72 w-full rounded-2xl object-cover"
                    />
                    <video
                      v-else-if="isVideoMessage(msg)"
                      :src="msg.attachment.file_url"
                      controls
                      preload="metadata"
                      class="max-h-72 w-full rounded-2xl bg-black"
                    ></video>
                    <audio
                      v-else-if="isAudioMessage(msg)"
                      :src="msg.attachment.file_url"
                      controls
                      preload="metadata"
                      class="w-full min-w-[220px]"
                    ></audio>
                    <a
                      v-else
                      :href="msg.attachment.file_url"
                      :download="msg.attachment.file_name || 'attachment'"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="flex min-w-[220px] items-center gap-3 rounded-2xl border px-3 py-2 transition hover:opacity-90"
                      :class="attachmentCardClass(msg)"
                    >
                      <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-black/10 text-lg font-semibold">
                        {{ fileExtensionLabel(msg.attachment) }}
                      </div>
                      <div class="min-w-0 flex-1">
                        <p class="truncate font-medium">{{ msg.attachment.file_name || 'Attachment' }}</p>
                        <p class="text-xs" :class="attachmentMetaClass(msg)">
                          {{ buildAttachmentPreviewLabel(msg.attachment) }}
                          <span v-if="msg.attachment.file_size"> · {{ formatFileSize(msg.attachment.file_size) }}</span>
                        </p>
                      </div>
                    </a>
                  </template>

                  <p v-if="msg.message" class="whitespace-pre-wrap break-words" :class="msg.attachment ? 'mt-2' : ''">
                    {{ msg.message }}
                  </p>
                </div>
                <div
                  class="mt-1 px-1 text-[10px]"
                  :class="msg.sender === session.user ? 'text-right text-gray-500' : 'text-left text-gray-500'"
                >
                  {{ formatTime(msg.timestamp) }}
                </div>
              </div>
            </div>
          </div>

          <div class="border-t bg-white px-2 py-2 sm:px-4">
            <input ref="fileInputRef" type="file" class="hidden" @change="handleAttachmentSelection" />

            <div v-if="uploadingAttachment || pendingAttachment" class="mb-2 flex items-center justify-between gap-3 rounded-2xl border border-gray-200 bg-gray-50 px-3 py-2">
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-gray-700">
                  {{ uploadingAttachment ? 'Uploading file...' : (pendingAttachment?.file_name || 'Attachment ready') }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ uploadingAttachment ? 'Please wait before sending' : buildPendingAttachmentMeta() }}
                </p>
              </div>

              <button
                v-if="pendingAttachment && !uploadingAttachment"
                type="button"
                class="flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 text-gray-500 transition hover:border-rose-300 hover:text-rose-500"
                @click="removePendingAttachment"
              >
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m6 6 12 12M18 6 6 18" stroke-linecap="round" />
                </svg>
              </button>
            </div>

            <div class="flex gap-2">
              <button
                type="button"
                class="flex h-10 w-10 items-center justify-center rounded-full border border-gray-300 bg-white text-gray-600 transition hover:border-green-400 hover:text-green-600 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!selectedUser || sending || uploadingAttachment"
                @click="openAttachmentPicker"
              >
                <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.44 11.05 12.25 20a6 6 0 1 1-8.49-8.48l9.19-8.95a4 4 0 0 1 5.66 5.65l-9.2 8.95a2 2 0 1 1-2.82-2.83l8.49-8.24" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>

              <textarea
                v-model="newMessage"
                rows="1"
                placeholder="Type..."
                class="flex-1 resize-none rounded-full border px-4 py-2 text-sm focus:ring-1 focus:ring-green-400"
                @keydown.enter.exact.prevent="sendMessage"
                @input="onTyping"
                @blur="stopTyping"
              />

              <button
                type="button"
                class="flex h-10 w-10 items-center justify-center rounded-full bg-green-500 text-white transition hover:bg-green-600 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!canSendMessage"
                @click="sendMessage"
              >
                <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                  <path d="M3.4 20.4 21 12 3.4 3.6 3.3 10l12.2 2-12.2 2 .1 6.4z" />
                </svg>
              </button>
            </div>
          </div>
        </template>
      </div>

      <CallUI
        v-if="currentCall && !isVideoCall"
        :call="currentCall"
        :duration-text="durationText"
        :incoming="Boolean(incomingCall && !activeCall)"
        :media-state="mediaState"
        :status="callStatus"
        @accept="acceptIncomingCall"
        @end="endCurrentCall"
        @reject="rejectIncomingCall"
        @toggle-mute="toggleMute"
        @toggle-speaker="toggleSpeaker"
        @toggle-camera="toggleCamera"
      />

      <div
        v-if="incomingCall && !activeCall"
        class="fixed right-4 top-4 z-50 w-[340px] rounded-3xl border border-emerald-200 bg-white p-4 shadow-2xl"
      >
        <p class="text-xs font-semibold uppercase tracking-[0.22em] text-green-600">Incoming Call</p>
        <p class="mt-2 text-lg font-semibold text-gray-900">{{ incomingCall.remoteName }}</p>
        <p class="mt-1 text-sm text-gray-500">
          {{ incomingCall.callType === 'video' ? 'Video call' : 'Audio call' }} ready to answer
        </p>
        <div class="mt-4 flex gap-2">
          <button class="flex-1 rounded-full bg-green-500 px-4 py-2 text-sm font-semibold text-white" @click="acceptIncomingCall">
            Accept
          </button>
          <button class="flex-1 rounded-full bg-rose-500 px-4 py-2 text-sm font-semibold text-white" @click="rejectIncomingCall">
            Reject
          </button>
        </div>
      </div>

      <VideoCallUI
        v-if="currentCall && isVideoCall"
        :call="currentCall"
        :duration-text="durationText"
        :incoming="Boolean(incomingCall && !activeCall)"
        :local-stream="localStream"
        :media-state="mediaState"
        :remote-stream="remoteStream"
        :status="callStatus"
        @accept="acceptIncomingCall"
        @end="endCurrentCall"
        @reject="rejectIncomingCall"
        @toggle-camera="toggleCamera"
        @toggle-mute="toggleMute"
        @toggle-screen-share="toggleScreenShare"
        @toggle-speaker="toggleSpeaker"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { createResource, frappeRequest } from 'frappe-ui'
import { useToast } from 'vue-toastification'

import CallUI from '@/Components/CallUI.vue'
import VideoCallUI from '@/Components/VideoCallUI.vue'
import { useCallManager } from '@/composables/useCallManager'
import { session } from '@/data/session'
import { connectSocket } from '@/socket'
import Sidebar from '../Components/sidebar.vue'

// Connect socket early so useCallManager can register its listeners
const socket = connectSocket()

const SELECTED_USER_KEY = 'selectedUserName'

const search = ref('')
const allUsers = ref([])
const selectedUser = ref(null)
const messageGroups = ref([])
const newMessage = ref('')
const sending = ref(false)
const loadingMessages = ref(false)
const uploadingAttachment = ref(false)
const messagesContainer = ref(null)
const fileInputRef = ref(null)
const lastMessageMap = ref({})
const lastOutgoingDraft = ref(null)
const pendingAttachment = ref(null)
const typingUsers = ref({})
const onlineUsers = ref([])
const lastSeen = ref(JSON.parse(localStorage.getItem('lastSeen') || '{}'))
const selectedUserName = ref(localStorage.getItem(SELECTED_USER_KEY) || '')
const recentCallLogs = ref([])
const recentCallSummary = ref({ call_count: 0, missed_calls: 0 })
const sidebarExpanded = ref(false)
const deletingCallId = ref('')
const deletingSelectedCallLogsState = ref(false)
const clearingCallLogs = ref(false)
const toast = useToast()

const currentUserName = computed(() => {
  const user = allUsers.value.find(entry => entry.name === session.user)
  if (user?.full_name) return user.full_name
  if (user?.first_name) return user.first_name
  return session.user ? session.user.split('@')[0] : 'User'
})

const currentUserInitials = computed(() => initials(currentUserName.value))
const canSendMessage = computed(
  () => Boolean(selectedUser.value)
    && !sending.value
    && !uploadingAttachment.value
    && Boolean(newMessage.value.trim() || pendingAttachment.value)
)

const unreadCount = computed(() => {
  const counts = {}
  for (const user of allUsers.value) {
    const lastSeenTime = lastSeen.value[user.name] || 0
    const lastMessageTime = Date.parse(lastMessageMap.value[user.name]?.timestamp || 0) || 0
    if (lastMessageTime > lastSeenTime && user.name !== selectedUser.value?.name) {
      counts[user.name] = 1
    }
  }
  return counts
})

const sidebarUsers = computed(() => {
  const self = {
    name: session.user,
    full_name: currentUserName.value,
    first_name: currentUserName.value,
  }
  return [self, ...allUsers.value]
})

const filteredUsers = computed(() => {
  const query = search.value.toLowerCase().trim()
  const users = [...sidebarUsers.value]

  const filtered = query
    ? users.filter(user =>
        (user.full_name || user.first_name || user.name).toLowerCase().includes(query)
      )
    : users

  return filtered.sort((left, right) => {
    const leftTime = Date.parse(lastMessageMap.value[left.name]?.timestamp || 0) || 0
    const rightTime = Date.parse(lastMessageMap.value[right.name]?.timestamp || 0) || 0
    return rightTime - leftTime
  })
})

const sidebarCallLogs = computed(() =>
  recentCallLogs.value.map(log => {
    const peer = resolveUser(log.peer)
    return {
      ...log,
      peer_name: peer.full_name || peer.first_name || peer.name || log.peer,
    }
  })
)

function resolveUser(userId) {
  return (
    allUsers.value.find(entry => entry.name === userId) || {
      name: userId,
      full_name: userId,
      first_name: userId,
    }
  )
}

const {
  activeCall,
  callLogs,
  callStatus,
  callSummary,
  currentCall,
  durationText,
  incomingCall,
  isInCall,
  isVideoCall,
  localStream,
  mediaState,
  remoteStream,
  acceptIncomingCall,
  endCurrentCall,
  refreshCallLogs,
  rejectIncomingCall,
  startCall,
  toggleCamera,
  toggleMute,
  toggleScreenShare,
  toggleSpeaker,
} = useCallManager({
  resolveUser,
  onCallStateChange: () => {
    refreshSidebarCallLogs().catch(() => null)
    if (selectedUser.value?.name) {
      refreshCallLogs(selectedUser.value.name).catch(() => null)
    }
  },
  onIncomingCall: call => {
    if (call?.remoteUser) {
      focusPeer(call.remoteUser)
    }
  },
})

const callStatusLabel = computed(() => {
  if (callStatus.value === 'connected') return `Connected · ${durationText.value}`
  if (callStatus.value === 'connecting') return 'Connecting'
  if (callStatus.value === 'incoming') return 'Incoming call'
  if (callStatus.value === 'ringing') return 'Ringing'
  return 'Idle'
})

function initials(name) {
  if (!name) return '?'
  return name
    .trim()
    .split(/\s+/)
    .map(part => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

const COLORS = ['#25D366', '#128C7E', '#075E54', '#34B7F1', '#0084ff', '#7b68ee', '#ff6b6b', '#ffa500']

function avatarColor(name) {
  let hash = 0
  for (const char of name || '') hash = char.charCodeAt(0) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
}

function formatTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatDateLabel(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  if (date.toDateString() === today.toDateString()) return 'Today'
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return date.toLocaleDateString([], {
    weekday: 'long',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function guessAttachmentKind(attachment) {
  const mimeType = (attachment?.mime_type || '').toLowerCase()
  if (mimeType.startsWith('image/')) return 'image'
  if (mimeType.startsWith('video/')) return 'video'
  if (mimeType.startsWith('audio/')) return 'audio'
  return attachment?.media_kind || 'file'
}

function normalizeAttachment(attachment) {
  if (!attachment?.file_url) return null

  return {
    file_name: attachment.file_name || attachment.file_url.split('/').pop() || 'Attachment',
    file_size: Number(attachment.file_size) || 0,
    file_url: attachment.file_url,
    media_kind: guessAttachmentKind(attachment),
    mime_type: attachment.mime_type || '',
  }
}

function buildAttachmentPreviewLabel(attachment) {
  if (!attachment) return ''
  if (attachment.media_kind === 'image') return 'Photo'
  if (attachment.media_kind === 'video') return 'Video'
  if (attachment.media_kind === 'audio') return 'Audio'
  return attachment.file_name || 'File'
}

function formatFileSize(size) {
  const bytes = Number(size) || 0
  if (!bytes) return '0 B'
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(bytes >= 10 * 1024 * 1024 ? 0 : 1)} MB`
  }
  if (bytes >= 1024) {
    return `${Math.round(bytes / 1024)} KB`
  }
  return `${bytes} B`
}

function formatMessagePreview(data) {
  const attachment = normalizeAttachment(data?.attachment)
  const text = typeof data?.message === 'string' ? data.message.trim() : ''
  return text || buildAttachmentPreviewLabel(attachment)
}

function normalizeMessageData(data) {
  const attachment = normalizeAttachment(data?.attachment)
  const message = typeof data?.message === 'string' ? data.message : ''

  return {
    attachment,
    message,
    message_type: data?.message_type || (attachment ? (message ? 'mixed' : 'attachment') : 'text'),
    preview_text: typeof data?.preview_text === 'string' && data.preview_text.trim()
      ? data.preview_text
      : formatMessagePreview({ attachment, message }),
    sender: data?.sender || '',
    timestamp: data?.timestamp || '',
  }
}

function normalizeMessageGroups(groups) {
  return (groups || []).map(group => ({
    ...group,
    messages: (group.messages || []).map(normalizeMessageData),
  }))
}

function isOwnMessage(message) {
  return message?.sender === session.user
}

function messageBubbleClass(message) {
  return isOwnMessage(message) ? 'bg-green-500 text-white' : 'bg-white text-gray-800'
}

function attachmentCardClass(message) {
  return isOwnMessage(message)
    ? 'border-white/20 bg-white/10 text-white'
    : 'border-gray-200 bg-gray-50 text-gray-800'
}

function attachmentMetaClass(message) {
  return isOwnMessage(message) ? 'text-white/70' : 'text-gray-500'
}

function fileExtensionLabel(attachment) {
  const extension = (attachment?.file_name || '').split('.').pop()
  if (!extension || extension === attachment?.file_name) return 'FI'
  return extension.slice(0, 2).toUpperCase()
}

function isImageMessage(message) {
  return message?.attachment?.media_kind === 'image'
}

function isVideoMessage(message) {
  return message?.attachment?.media_kind === 'video'
}

function isAudioMessage(message) {
  return message?.attachment?.media_kind === 'audio'
}

function buildPendingAttachmentMeta() {
  if (!pendingAttachment.value) return ''
  const previewLabel = buildAttachmentPreviewLabel(pendingAttachment.value)
  const fileSize = pendingAttachment.value.file_size ? ` · ${formatFileSize(pendingAttachment.value.file_size)}` : ''
  return `${previewLabel}${fileSize}`
}

function extractErrorMessage(error, fallback) {
  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message
  }

  if (Array.isArray(error?.messages) && error.messages.length) {
    return error.messages[0]
  }

  if (typeof error?._server_messages === 'string') {
    try {
      const serverMessages = JSON.parse(error._server_messages)
      const firstMessage = serverMessages[0]
      if (typeof firstMessage === 'string') {
        try {
          const parsedMessage = JSON.parse(firstMessage)
          if (typeof parsedMessage?.message === 'string' && parsedMessage.message.trim()) {
            return parsedMessage.message
          }
        } catch {
          if (firstMessage.trim()) return firstMessage
        }
      }
    } catch {
      // no-op
    }
  }

  return fallback
}

async function refreshSidebarCallLogs() {
  try {
    const response = await frappeRequest({
      url: 'fun.api.get_call_logs',
      params: { limit: 10 },
    })

    recentCallLogs.value = response.logs || []
    recentCallSummary.value = response.summary || { call_count: 0, missed_calls: 0 }
  } catch (error) {
    console.error('[chat] failed to refresh sidebar call logs', error)
  }
}

async function deleteCallLog(callId) {
  if (!callId || deletingCallId.value || clearingCallLogs.value || deletingSelectedCallLogsState.value) return

  if (!window.confirm('Delete this call log?')) return

  deletingCallId.value = callId

  try {
    await frappeRequest({
      url: 'fun.api.delete_call_log',
      params: { call_id: callId },
    })

    await refreshSidebarCallLogs()
    if (selectedUser.value?.name) {
      await refreshCallLogs(selectedUser.value.name).catch(() => null)
    }
    toast.success('Call log deleted')
  } catch (error) {
    console.error('[chat] failed to delete call log', error)
    toast.error(extractErrorMessage(error, 'Unable to delete call log'))
  } finally {
    deletingCallId.value = ''
  }
}

async function deleteSelectedCallLogs(callIds) {
  const normalizedCallIds = Array.isArray(callIds)
    ? [...new Set(callIds.filter(Boolean))]
    : []

  if (!normalizedCallIds.length || deletingSelectedCallLogsState.value || clearingCallLogs.value || deletingCallId.value) {
    return
  }

  const confirmationMessage = normalizedCallIds.length === 1
    ? 'Delete 1 selected call log?'
    : `Delete ${normalizedCallIds.length} selected call logs?`

  if (!window.confirm(confirmationMessage)) return

  deletingSelectedCallLogsState.value = true

  try {
    let deletedCount = 0
    let skippedActiveCount = 0
    let failedCount = 0
    let lastError = null

    for (const callId of normalizedCallIds) {
      try {
        await frappeRequest({
          url: 'fun.api.delete_call_log',
          params: { call_id: callId },
        })
        deletedCount += 1
      } catch (error) {
        const message = extractErrorMessage(error, '')
        if (/active calls cannot be deleted/i.test(message)) {
          skippedActiveCount += 1
        } else {
          failedCount += 1
          lastError = error
        }
      }
    }

    await refreshSidebarCallLogs()
    if (selectedUser.value?.name) {
      await refreshCallLogs(selectedUser.value.name).catch(() => null)
    }

    if (deletedCount) {
      toast.success(
        deletedCount === 1
          ? '1 call log deleted'
          : `${deletedCount} call logs deleted`
      )
    } else {
      toast.info('No call logs were deleted')
    }

    if (skippedActiveCount) {
      toast.info(
        skippedActiveCount === 1
          ? '1 active call log was skipped'
          : `${skippedActiveCount} active call logs were skipped`
      )
    }

    if (failedCount) {
      toast.error(
        failedCount === 1
          ? extractErrorMessage(lastError, '1 call log could not be deleted')
          : `${failedCount} call logs could not be deleted`
      )
    }
  } catch (error) {
    console.error('[chat] failed to delete selected call logs', error)
    toast.error(extractErrorMessage(error, 'Unable to delete selected call logs'))
  } finally {
    deletingSelectedCallLogsState.value = false
  }
}

async function clearAllCallLogs() {
  if (!recentCallLogs.value.length || clearingCallLogs.value || deletingCallId.value || deletingSelectedCallLogsState.value) return

  if (!window.confirm('Delete all call logs?')) return

  clearingCallLogs.value = true

  try {
    const response = await frappeRequest({
      url: 'fun.api.clear_call_logs',
      params: {},
    })

    await refreshSidebarCallLogs()
    if (selectedUser.value?.name) {
      await refreshCallLogs(selectedUser.value.name).catch(() => null)
    }

    if (response?.deleted_count) {
      toast.success(
        response.deleted_count === 1
          ? '1 call log deleted'
          : `${response.deleted_count} call logs deleted`
      )
    } else {
      toast.info('No call logs were deleted')
    }

    if (response?.skipped_active_count) {
      toast.info(
        response.skipped_active_count === 1
          ? '1 active call log was skipped'
          : `${response.skipped_active_count} active call logs were skipped`
      )
    }
  } catch (error) {
    console.error('[chat] failed to clear call logs', error)
    toast.error(extractErrorMessage(error, 'Unable to clear call logs'))
  } finally {
    clearingCallLogs.value = false
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}


createResource({
  url: 'fun.api.get_users',
  auto: true,
  onSuccess(data) {
    allUsers.value = data || []
  },
})

createResource({
  url: 'fun.api.get_conversations',
  auto: true,
  onSuccess(data) {
    const map = {}
    for (const conversation of data || []) {
      map[conversation.peer] = {
        last_message: conversation.last_message,
        timestamp: conversation.timestamp,
      }
    }
    lastMessageMap.value = map
  },
})

const messagesResource = createResource({
  url: 'fun.api.get_messages',
  onSuccess(data) {
    messageGroups.value = normalizeMessageGroups(data || [])
    loadingMessages.value = false
    scrollToBottom()
  },
  onError() {
    loadingMessages.value = false
  },
})


const sendResource = createResource({
  url: 'fun.api.send_message',
  onSuccess(data) {
    const normalizedMessage = normalizeMessageData(data)
    appendMessage(normalizedMessage, data)
    sending.value = false
    lastOutgoingDraft.value = null
    const peer = data.receiver === session.user ? data.sender : data.receiver
    lastMessageMap.value = {
      ...lastMessageMap.value,
      [peer]: { last_message: normalizedMessage.preview_text, timestamp: data.timestamp },
    }
  },
  onError(error) {
    sending.value = false
    if (lastOutgoingDraft.value) {
      newMessage.value = lastOutgoingDraft.value.message
      pendingAttachment.value = lastOutgoingDraft.value.attachment
      lastOutgoingDraft.value = null
    }
    toast.error(extractErrorMessage(error, 'Unable to send message'))
  },
})

function appendMessage(data, source = data) {
  const groups = JSON.parse(JSON.stringify(messageGroups.value))
  const lastGroup = groups[groups.length - 1]
  const nextMessage = normalizeMessageData(data)

  if (lastGroup && lastGroup.conversation_name === source.conversation_name) {
    const alreadyPresent = lastGroup.messages.some(
      message =>
        message.sender === nextMessage.sender &&
        message.message === nextMessage.message &&
        JSON.stringify(message.attachment || null) === JSON.stringify(nextMessage.attachment || null) &&
        message.timestamp === nextMessage.timestamp
    )

    if (alreadyPresent) {
      messageGroups.value = groups
      scrollToBottom()
      return
    }

    lastGroup.messages = [
      ...lastGroup.messages,
      nextMessage,
    ]
  } else {
    groups.push({
      conversation_name: source.conversation_name,
      start_date: source.start_date,
      messages: [nextMessage],
    })
  }

  messageGroups.value = groups
  scrollToBottom()
}

function persistSelectedUser(userName = '') {
  selectedUserName.value = userName
  if (userName) {
    localStorage.setItem(SELECTED_USER_KEY, userName)
  } else {
    localStorage.removeItem(SELECTED_USER_KEY)
  }
}

function updateLastSeen(userName) {
  if (!userName) return
  lastSeen.value = { ...lastSeen.value, [userName]: Date.now() }
  localStorage.setItem('lastSeen', JSON.stringify(lastSeen.value))
}

function loadSelectedChat(userName) {
  if (!userName) {
    messageGroups.value = []
    loadingMessages.value = false
    return
  }

  messageGroups.value = []
  loadingMessages.value = true
  messagesResource.submit({ other_user: userName })
  refreshCallLogs(userName).catch(() => null)
  updateLastSeen(userName)
}

function focusPeer(userName) {
  if (!userName) return
  const nextUser = resolveUser(userName)
  selectedUser.value = nextUser
  persistSelectedUser(nextUser.name)
}

function selectUser(user) {
  if (!user?.name) return
  focusPeer(user.name)
}

async function uploadChatFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/method/fun.api.upload_chat_file', {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || '',
      'X-Requested-With': 'XMLHttpRequest',
    },
    credentials: 'include',
    body: formData,
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw payload
  }

  return normalizeAttachment(payload.message || payload)
}

function openAttachmentPicker() {
  if (!selectedUser.value || sending.value || uploadingAttachment.value) return
  fileInputRef.value?.click()
}

function removePendingAttachment() {
  pendingAttachment.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

async function handleAttachmentSelection(event) {
  const selectedFile = event.target?.files?.[0]
  if (!selectedFile) return

  uploadingAttachment.value = true

  try {
    pendingAttachment.value = await uploadChatFile(selectedFile)
  } catch (error) {
    console.error('[chat] failed to upload attachment', error)
    toast.error(extractErrorMessage(error, 'Unable to upload file'))
  } finally {
    uploadingAttachment.value = false
    if (event.target) {
      event.target.value = ''
    }
  }
}

function sendMessage() {
  const text = newMessage.value.trim()
  const attachment = pendingAttachment.value ? { ...pendingAttachment.value } : null

  if ((!text && !attachment) || sending.value || uploadingAttachment.value || !selectedUser.value) return

  sending.value = true
  lastOutgoingDraft.value = {
    attachment,
    message: newMessage.value,
  }
  newMessage.value = ''
  pendingAttachment.value = null
  stopTyping()

  const payload = {
    receiver: selectedUser.value.name,
    message: text,
  }
  if (attachment) {
    payload.attachment = JSON.stringify(attachment)
  }
  sendResource.submit(payload)
}

let typingTimeout = null
const onTypingEvent = data => {
  typingUsers.value = { ...typingUsers.value, [data.from]: true }
}
const onStopTypingEvent = data => {
  typingUsers.value = { ...typingUsers.value, [data.from]: false }
}
const onUserOnline = data => {
  if (!onlineUsers.value.includes(data.user)) {
    onlineUsers.value = [...onlineUsers.value, data.user]
  }
}
const onUserOffline = data => {
  onlineUsers.value = onlineUsers.value.filter(user => user !== data.user)
}

function onTyping() {
  if (!selectedUser.value || !socket) return
  socket.emit('typing', { to: selectedUser.value.name })
  window.clearTimeout(typingTimeout)
  typingTimeout = window.setTimeout(stopTyping, 2000)
}

function stopTyping() {
  if (!selectedUser.value || !socket) return
  socket.emit('stop_typing', { to: selectedUser.value.name })
  window.clearTimeout(typingTimeout)
}

async function handleIncomingMessage(data) {
  if (!data?.sender) {
    return
  }
  const normalizedMessage = normalizeMessageData(data)
  const peer = data.sender === session.user ? data.receiver : data.sender
  lastMessageMap.value = {
    ...lastMessageMap.value,
    [peer]: { last_message: normalizedMessage.preview_text, timestamp: data.timestamp },
  }

  if (!selectedUser.value) {
    return
  }
  if (peer !== selectedUser.value.name) {
    return
  }

  messagesResource.submit({ other_user: peer })
}

function handleRealtimeEnvelope(data) {
  if (!data?.event) return

  if (data.event === 'new_message') {
    handleIncomingMessage(data.message)
    return
  }

  if (data.event === 'typing') {
    onTypingEvent(data.data)
    return
  }

  if (data.event === 'stop_typing') {
    onStopTypingEvent(data.data)
  }
}

function startVoiceCall() {
  if (!selectedUser.value) return
  startCall(selectedUser.value, 'audio').catch(console.error)
}

function startVideoCall() {
  if (!selectedUser.value) return
  startCall(selectedUser.value, 'video').catch(console.error)
}

function logout() {
  session.logout.submit()
}

watch(
  () => selectedUser.value?.name,
  userName => {
    if (userName) {
      loadSelectedChat(userName)
    } else {
      messageGroups.value = []
      loadingMessages.value = false
    }
  },
  { immediate: true }
)

watch(
  allUsers,
  users => {
    const savedUserName = selectedUserName.value
    if (!savedUserName) {
      if (selectedUser.value?.name && !users.some(user => user.name === selectedUser.value.name)) {
        selectedUser.value = null
      }
      return
    }

    const matchedUser = users.find(user => user.name === savedUserName)
    if (!matchedUser) {
      if (users.length) {
        selectedUser.value = null
        persistSelectedUser('')
      }
      return
    }

    if (selectedUser.value?.name !== matchedUser.name) {
      selectedUser.value = matchedUser
      return
    }

    selectedUser.value = matchedUser
  },
  { immediate: true }
)

onMounted(() => {
  refreshSidebarCallLogs().catch(() => null)
  if (!socket) return

  socket.on('new_message', handleIncomingMessage)
  socket.on('realtime', handleRealtimeEnvelope)
  socket.on('typing', onTypingEvent)
  socket.on('stop_typing', onStopTypingEvent)
  socket.on('user_online', onUserOnline)
  socket.on('user_offline', onUserOffline)
})

onUnmounted(() => {
  if (socket) {
    socket.off('new_message', handleIncomingMessage)
    socket.off('realtime', handleRealtimeEnvelope)
    socket.off('typing', onTypingEvent)
    socket.off('stop_typing', onStopTypingEvent)
    socket.off('user_online', onUserOnline)
    socket.off('user_offline', onUserOffline)
  }
})
</script>
