<template>
  <div class="flex h-screen overflow-hidden bg-gray-100">
    <div
      class="fixed z-20 flex h-full w-72 transform flex-col border-r border-gray-200 bg-white transition-transform duration-300 sm:w-80 md:relative md:translate-x-0"
      :class="selectedUser ? '-translate-x-full md:translate-x-0' : 'translate-x-0'"
    >
      <div class="flex items-center justify-between bg-green-600 px-4 py-3">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/30 text-sm font-bold text-white">
            {{ currentUserInitials }}
          </div>
          <span class="max-w-[120px] truncate text-sm font-semibold text-white">
            {{ currentUserName }}
          </span>
        </div>
        <button class="text-xs text-white/80 hover:text-white" @click="logout">Logout</button>
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

        <div class="border-b bg-white px-4 py-3">
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
        </div>

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
                :class="msg.sender === session.user ? 'bg-green-500 text-white' : 'bg-white text-gray-800'"
              >
                {{ msg.message }}
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

        <div class="flex gap-2 border-t bg-white px-2 py-2 sm:px-4">
          <textarea
            v-model="newMessage"
            rows="1"
            placeholder="Type..."
            class="flex-1 resize-none rounded-full border px-4 py-2 text-sm focus:ring-1 focus:ring-green-400"
            @keydown.enter.exact.prevent="sendMessage"
            @input="onTyping"
            @blur="stopTyping"
          />
          <button class="h-10 w-10 rounded-full bg-green-500 text-white" @click="sendMessage">➤</button>
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
    />

    <div
      v-if="incomingCall && !activeCall"
      class="fixed right-4 top-4 z-50 w-[320px] rounded-3xl border border-white/20 bg-white p-4 shadow-2xl"
    >
      <p class="text-xs font-semibold uppercase tracking-[0.22em] text-green-600">Incoming Call</p>
      <p class="mt-2 text-lg font-semibold text-gray-900">{{ incomingCall.remoteName }}</p>
      <p class="mt-1 text-sm text-gray-500">{{ incomingCall.callType === 'video' ? 'Video call' : 'Audio call' }}</p>
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
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { createResource } from 'frappe-ui'

import CallUI from '@/Components/CallUI.vue'
import VideoCallUI from '@/Components/VideoCallUI.vue'
import { useCallManager } from '@/composables/useCallManager'
import { session } from '@/data/session'
import { useSocket } from '@/socket'

const SELECTED_USER_KEY = 'selectedUserName'

const search = ref('')
const allUsers = ref([])
const selectedUser = ref(null)
const messageGroups = ref([])
const newMessage = ref('')
const sending = ref(false)
const loadingMessages = ref(false)
const messagesContainer = ref(null)
const lastMessageMap = ref({})
const typingUsers = ref({})
const onlineUsers = ref([])
const lastSeen = ref(JSON.parse(localStorage.getItem('lastSeen') || '{}'))
const selectedUserName = ref(localStorage.getItem(SELECTED_USER_KEY) || '')

const currentUserName = computed(() => {
  const user = allUsers.value.find(entry => entry.name === session.user)
  if (user?.full_name) return user.full_name
  if (user?.first_name) return user.first_name
  return session.user ? session.user.split('@')[0] : 'User'
})

const currentUserInitials = computed(() => initials(currentUserName.value))

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
    if (selectedUser.value?.name) {
      refreshCallLogs(selectedUser.value.name).catch(() => null)
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
    messageGroups.value = data || []
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
    appendMessage(data)
    sending.value = false
    const peer = data.receiver === session.user ? data.sender : data.receiver
    lastMessageMap.value = {
      ...lastMessageMap.value,
      [peer]: { last_message: data.message, timestamp: data.timestamp },
    }
  },
  onError() {
    sending.value = false
  },
})

function appendMessage(data) {
  const groups = JSON.parse(JSON.stringify(messageGroups.value))
  const lastGroup = groups[groups.length - 1]
  const nextMessage = {
    sender: data.sender,
    message: data.message,
    timestamp: data.timestamp,
  }

  if (lastGroup && lastGroup.conversation_name === data.conversation_name) {
    const alreadyPresent = lastGroup.messages.some(
      message =>
        message.sender === nextMessage.sender &&
        message.message === nextMessage.message &&
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
      conversation_name: data.conversation_name,
      start_date: data.start_date,
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

function selectUser(user) {
  if (!user?.name) return
  selectedUser.value = resolveUser(user.name)
  persistSelectedUser(user.name)
}

function sendMessage() {
  const text = newMessage.value.trim()
  if (!text || sending.value || !selectedUser.value) return
  sending.value = true
  newMessage.value = ''
  stopTyping()
  sendResource.submit({ receiver: selectedUser.value.name, message: text })
}

let typingTimeout = null
let socket = null
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
  console.debug('[chat] incoming message', data)
  const peer = data.sender === session.user ? data.receiver : data.sender
  lastMessageMap.value = {
    ...lastMessageMap.value,
    [peer]: { last_message: data.message, timestamp: data.timestamp },
  }

  if (!selectedUser.value) return
  if (peer !== selectedUser.value.name) return

  appendMessage(data)
  await nextTick()
}

function handleRealtimeEnvelope(data) {
  if (!data?.event) return
  console.debug('[chat] realtime envelope', data)

  if (data.event === 'new_message') {
    handleIncomingMessage(data.data)
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
  socket = useSocket()
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
